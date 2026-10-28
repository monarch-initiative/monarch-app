"""Utilities for building case-phenotype matrices."""

from typing import Any, Dict, List
from monarch_py.datamodels.model import (
    CasePhenotypeMatrixResponse,
    CaseEntity,
    CasePhenotype,
    HistoPhenoBin,
    CasePhenotypeCellData,
)
from monarch_py.datamodels.solr import HistoPhenoKeys, HISTOPHENO_BIN_LABELS
from monarch_py.utils.entity_grid_utils import bin_members, make_cell_key, parse_bin_facets


def build_matrix(
    disease_id: str,
    disease_name: str,
    case_docs: List[dict],
    phenotype_docs: List[dict],
    facets: Dict[str, Any],
) -> CasePhenotypeMatrixResponse:
    """Build case-phenotype matrix from Solr documents.

    Args:
        disease_id: The MONDO ID of the disease being queried
        disease_name: Human-readable name of the disease
        case_docs: List of CaseToDiseaseAssociation Solr documents
        phenotype_docs: List of CaseToPhenotypicFeatureAssociation Solr documents
        facets: The `facets` block of the phenotype query's JSON Facet response

    Returns:
        CasePhenotypeMatrixResponse with cases, phenotypes, bins, and cells
    """
    bin_ids = [key.value for key in HistoPhenoKeys]
    bin_counts, phenotype_bins = parse_bin_facets(facets, bin_ids)

    cases = _build_cases(case_docs, disease_id)
    case_map = {c.id: c for c in cases}
    phenotypes = _build_phenotypes(phenotype_docs, phenotype_bins)
    cells = _build_cells(phenotype_docs, case_map)
    bins = _build_bins(facets, bin_counts, bin_ids)

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


def _build_phenotypes(
    phenotype_docs: List[dict],
    phenotype_bins: Dict[str, str],
) -> List[CasePhenotype]:
    """Extract unique phenotypes and attach their HistoPheno bin.

    Args:
        phenotype_docs: List of CaseToPhenotypicFeatureAssociation Solr documents
        phenotype_bins: Phenotype ID -> bin ID, from `parse_bin_facets`

    Returns:
        List of CasePhenotype objects, deduplicated by phenotype ID. Phenotypes in no
        bin are dropped, as they were when bins came from the closure field.
    """
    seen_phenotypes: Dict[str, CasePhenotype] = {}

    for doc in phenotype_docs:
        phenotype_id = doc.get("object")
        if not phenotype_id or phenotype_id in seen_phenotypes:
            continue

        bin_id = phenotype_bins.get(phenotype_id)
        if bin_id is None:
            continue

        seen_phenotypes[phenotype_id] = CasePhenotype(
            id=phenotype_id,
            label=doc.get("object_label"),
            bin_id=bin_id,
        )

    return list(seen_phenotypes.values())


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
            id=cell_key,
            present=True,
            negated=doc.get("negated"),
            onset_qualifier=doc.get("onset_qualifier"),
            onset_qualifier_label=doc.get("onset_qualifier_label"),
            publications=doc.get("publications"),
        )
        cells[cell_key] = cell

    return cells


def _build_bins(
    facets: Dict[str, Any],
    bin_counts: Dict[str, int],
    bin_ids: List[str],
) -> List[HistoPhenoBin]:
    """Build bin list from the phenotype query's bin facet.

    Args:
        facets: The `facets` block of the phenotype query's JSON Facet response
        bin_counts: Bin ID -> association count, from `parse_bin_facets`
        bin_ids: Ordered HistoPheno bin IDs

    Returns:
        List of HistoPhenoBin objects in HistoPhenoKeys order
    """
    # A phenotype under several bins is listed under each of them here, which is what
    # the previous closure scan did for `phenotype_ids` (unlike `bin_id` on the
    # phenotype itself, where the first bin in order wins).
    members = bin_members(facets, bin_ids)

    return [
        HistoPhenoBin(
            id=bin_id,
            label=HISTOPHENO_BIN_LABELS.get(bin_id, bin_id),
            phenotype_count=bin_counts.get(bin_id, 0),
            phenotype_ids=members.get(bin_id, []),
        )
        for bin_id in bin_ids
    ]
