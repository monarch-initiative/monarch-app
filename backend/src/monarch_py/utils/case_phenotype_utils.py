"""Utilities for building case-phenotype matrices."""
from typing import Dict, List, Optional, Set
from monarch_py.datamodels.model import (
    CasePhenotypeMatrixResponse,
    CaseEntity,
    CasePhenotype,
    HistoPhenoBin,
    CasePhenotypeCellData,
)
from monarch_py.datamodels.solr import HistoPhenoKeys, HISTOPHENO_BIN_LABELS


def build_matrix(
    disease_id: str,
    disease_name: str,
    case_docs: List[dict],
    phenotype_docs: List[dict],
    facet_counts: Dict[str, int],
) -> CasePhenotypeMatrixResponse:
    """Build case-phenotype matrix from Solr documents.

    Args:
        disease_id: The MONDO ID of the disease being queried
        disease_name: Human-readable name of the disease
        case_docs: List of CaseToDiseaseAssociation Solr documents
        phenotype_docs: List of CaseToPhenotypicFeatureAssociation Solr documents
        facet_counts: Dict of facet query results (e.g. 'object_closure:"UPHENO:xxx"': count)

    Returns:
        CasePhenotypeMatrixResponse with cases, phenotypes, bins, and cells
    """
    cases = _build_cases(case_docs, disease_id)
    case_map = {c.id: c for c in cases}
    phenotypes, phenotype_to_bin = _build_phenotypes(phenotype_docs)
    cells = _build_cells(phenotype_docs, case_map)
    bins = _build_bins(phenotype_docs, facet_counts)

    return CasePhenotypeMatrixResponse(
        disease_id=disease_id,
        disease_name=disease_name,
        total_cases=len(cases),
        total_phenotypes=len(phenotypes),
        cases=cases,
        phenotypes=phenotypes,
        bins=bins,
        cells=cells,
    )


def _build_cases(case_docs: List[dict], query_disease_id: str) -> List[CaseEntity]:
    """Extract unique cases and determine direct/indirect status.

    Args:
        case_docs: List of CaseToDiseaseAssociation Solr documents
        query_disease_id: The disease ID from the original query

    Returns:
        List of CaseEntity objects, deduplicated by case ID
    """
    seen_cases: Dict[str, CaseEntity] = {}

    for doc in case_docs:
        case_id = doc.get("subject")
        if not case_id or case_id in seen_cases:
            continue

        case_disease_id = doc.get("object")
        is_direct = case_disease_id == query_disease_id

        case = CaseEntity(
            id=case_id,
            label=doc.get("subject_label"),
            is_direct=is_direct,
            source_disease_id=None if is_direct else case_disease_id,
            source_disease_label=None if is_direct else doc.get("object_label"),
        )
        seen_cases[case_id] = case

    return list(seen_cases.values())


def _build_phenotypes(phenotype_docs: List[dict]) -> tuple[List[CasePhenotype], Dict[str, str]]:
    """Extract unique phenotypes and assign to HistoPheno bins.

    Args:
        phenotype_docs: List of CaseToPhenotypicFeatureAssociation Solr documents

    Returns:
        Tuple of (list of CasePhenotype objects, mapping of phenotype_id to bin_id)
    """
    seen_phenotypes: Dict[str, CasePhenotype] = {}
    phenotype_to_bin: Dict[str, str] = {}
    bin_ids = {key.value for key in HistoPhenoKeys}

    for doc in phenotype_docs:
        phenotype_id = doc.get("object")
        if not phenotype_id or phenotype_id in seen_phenotypes:
            continue

        object_closure = doc.get("object_closure", [])
        bin_id = _find_bin_for_phenotype(object_closure, bin_ids)

        if bin_id is None:
            continue

        phenotype = CasePhenotype(
            id=phenotype_id,
            label=doc.get("object_label"),
            bin_id=bin_id,
        )
        seen_phenotypes[phenotype_id] = phenotype
        phenotype_to_bin[phenotype_id] = bin_id

    return list(seen_phenotypes.values()), phenotype_to_bin


def _find_bin_for_phenotype(object_closure: List[str], bin_ids: Set[str]) -> Optional[str]:
    """Find the HistoPheno bin for a phenotype based on its closure.

    Uses the HistoPhenoKeys enum order to ensure consistent assignment
    when a phenotype could belong to multiple bins.

    Args:
        object_closure: List of ancestor term IDs for the phenotype
        bin_ids: Set of valid HistoPheno bin IDs

    Returns:
        The bin ID if found, None otherwise
    """
    closure_set = set(object_closure)
    intersection = closure_set & bin_ids

    if not intersection:
        return None

    # Return first match in HistoPhenoKeys order for consistency
    for key in HistoPhenoKeys:
        if key.value in intersection:
            return key.value

    return intersection.pop()


def _build_cells(phenotype_docs: List[dict], case_map: Dict[str, CaseEntity]) -> Dict[str, CasePhenotypeCellData]:
    """Build cell data for each case-phenotype pair.

    Args:
        phenotype_docs: List of CaseToPhenotypicFeatureAssociation Solr documents
        case_map: Dict mapping case IDs to CaseEntity objects

    Returns:
        Dict mapping cell keys (case_id:phenotype_id) to CasePhenotypeCellData
    """
    cells: Dict[str, CasePhenotypeCellData] = {}

    for doc in phenotype_docs:
        case_id = doc.get("subject")
        phenotype_id = doc.get("object")

        if not case_id or not phenotype_id:
            continue
        if case_id not in case_map:
            continue

        cell_key = make_cell_key(case_id, phenotype_id)
        cell = CasePhenotypeCellData(
            present=True,
            negated=doc.get("negated"),
            onset_qualifier=doc.get("onset_qualifier"),
            onset_qualifier_label=doc.get("onset_qualifier_label"),
            publications=doc.get("publications"),
        )
        cells[cell_key] = cell

    return cells


def _build_bins(phenotype_docs: List[dict], facet_counts: Dict[str, int]) -> List[HistoPhenoBin]:
    """Build bin list with phenotype IDs from Solr documents.

    Args:
        phenotype_docs: List of CaseToPhenotypicFeatureAssociation Solr documents
        facet_counts: Dict of facet query results

    Returns:
        List of HistoPhenoBin objects with phenotype_ids populated
    """
    # Collect phenotypes per bin by checking closures
    bin_phenotypes: Dict[str, Set[str]] = {key.value: set() for key in HistoPhenoKeys}

    for doc in phenotype_docs:
        phenotype_id = doc.get("object")
        if not phenotype_id:
            continue
        closure = set(doc.get("object_closure", []))

        # Add phenotype to ALL matching bins (not just first)
        for key in HistoPhenoKeys:
            if key.value in closure:
                bin_phenotypes[key.value].add(phenotype_id)

    bins = []

    for key in HistoPhenoKeys:
        bin_id = key.value
        facet_key = f'object_closure:"{bin_id}"'
        count = facet_counts.get(facet_key, 0)

        bin_obj = HistoPhenoBin(
            id=bin_id,
            label=HISTOPHENO_BIN_LABELS.get(bin_id, bin_id),
            phenotype_count=count,
            phenotype_ids=sorted(bin_phenotypes[bin_id]),
        )
        bins.append(bin_obj)

    return bins


def make_cell_key(case_id: str, phenotype_id: str) -> str:
    """Create a cell key for looking up cell data.

    Args:
        case_id: The case/patient ID
        phenotype_id: The phenotype ID

    Returns:
        Cell key in format "case_id:phenotype_id"
    """
    return f"{case_id}:{phenotype_id}"
