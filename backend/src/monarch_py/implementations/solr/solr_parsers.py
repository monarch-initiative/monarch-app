from typing import Dict, List

from loguru import logger
from pydantic import ValidationError

from monarch_py.datamodels.model import (
    Association,
    CompactAssociation,
    CompactAssociationResults,
    AssociationCount,
    AssociationCountList,
    AssociationDirectionEnum,
    AssociationResults,
    AssociationTableResults,
    DirectionalAssociation,
    Entity,
    FacetField,
    FacetValue,
    HistoBin,
    HistoPheno,
    Mapping,
    MappingResults,
    SearchResult,
    SearchResults,
)
from monarch_py.datamodels.solr import HistoPhenoKeys, SolrQueryResult
from monarch_py.service.curie_service import converter
from monarch_py.implementations.solr.solr_query_utils import build_association_count_suffixes
from monarch_py.utils.association_type_utils import get_association_type_mapping_by_query_string
from monarch_py.utils.utils import get_links_for_field, get_provided_by_link

####################
# Parser functions #
####################


def parse_associations(
    query_result: SolrQueryResult,
    compact: bool = False,
    offset: int = 0,
    limit: int = 20,
) -> AssociationResults:
    associations = []
    total = query_result.response.num_found
    if compact:
        associations = [
            CompactAssociation(
                category=doc.get("category"),
                subject=doc.get("subject"),
                subject_label=doc.get("subject_label"),
                predicate=doc.get("predicate"),
                object=doc.get("object"),
                object_label=doc.get("object_label"),
                negated=doc.get("negated"),
            )
            for doc in query_result.response.docs
        ]
        return CompactAssociationResults(
            items=associations,
            limit=limit,
            offset=offset,
            total=total,
            facet_fields=convert_facet_fields(query_result.facet_counts.facet_fields),
            facet_queries=convert_facet_queries(query_result.facet_counts.facet_queries),
        )
    else:
        for doc in query_result.response.docs:
            try:
                association = Association(**doc)
            except ValidationError:
                logger.error(f"Validation error for {doc}")
                raise ValidationError
            association.provided_by_link = (
                get_provided_by_link(association.provided_by) if association.provided_by else []
            )
            association.has_evidence_links = (
                get_links_for_field(association.has_evidence) if association.has_evidence else []
            )
            association.publications_links = (
                get_links_for_field(association.publications) if association.publications else []
            )
            associations.append(association)
        return AssociationResults(
            items=associations,
            limit=limit,
            offset=offset,
            total=total,
            facet_fields=convert_facet_fields(query_result.facet_counts.facet_fields),
            facet_queries=convert_facet_queries(query_result.facet_counts.facet_queries),
        )


def parse_association_counts(query_result: SolrQueryResult, entities: List[str]) -> AssociationCountList:
    """Parse facet query results into AssociationCount objects with direct, closure, and ortholog counts.

    Args:
        query_result: Solr query result containing facet queries
        entities: List of entity IDs (primary entity first, then orthologs)
    """
    has_orthologs = len(entities) > 1
    suffixes = build_association_count_suffixes(entities)

    # Map from suffix key to (count_level, is_subject_direction)
    suffix_metadata = {
        "direct_subject": ("direct", True),
        "direct_object": ("direct", False),
        "closure_subject": ("closure", True),
        "closure_object": ("closure", False),
        "orthologs_subject": ("orthologs", True),
        "orthologs_object": ("orthologs", False),
    }

    # Collect counts into a dict keyed by (label, category)
    # Each entry accumulates direct, closure, and ortholog counts
    count_data: Dict[str, Dict] = {}

    def _ensure_entry(label: str, category: str):
        if label not in count_data:
            count_data[label] = {"category": category, "direct": 0, "closure": 0, "orthologs": 0}

    for k, v in query_result.facet_counts.facet_queries.items():
        if v == 0:
            continue

        # Determine which suffix matches and which count level it represents
        count_level = None
        is_subject_direction = None
        original_query = None

        for suffix_key, suffix_str in suffixes.all_suffixes.items():
            if k.endswith(suffix_str):
                original_query = k.replace(f" {suffix_str}", "").lstrip("(").rstrip(")")
                count_level, is_subject_direction = suffix_metadata[suffix_key]
                break

        if count_level is None:
            raise ValueError(f"Unexpected facet query when building association counts: {k}")

        agm = get_association_type_mapping_by_query_string(original_query)
        label = agm.subject_label if is_subject_direction else agm.object_label

        _ensure_entry(label, agm.category)

        # For symmetric associations, sum both directions; otherwise set the value
        if agm.symmetric and count_data[label][count_level] > 0:
            count_data[label][count_level] += v
        else:
            count_data[label][count_level] = v

    # Build AssociationCount objects
    items = []
    for label, data in count_data.items():
        items.append(
            AssociationCount(
                label=label,
                count=data["closure"],
                count_direct=data["direct"],
                count_with_orthologs=data["orthologs"] if has_orthologs else None,
                category=data["category"],
            )
        )

    return AssociationCountList(items=items)


def parse_entity(solr_document: Dict) -> Entity:
    try:
        entity = Entity(**solr_document)
        entity.uri = converter.expand(entity.id)
    except ValidationError:
        logger.error(f"Validation error for {solr_document}")
        raise
    return entity


def parse_association_table(
    query_result: SolrQueryResult,
    entity: List[str],
    offset: int,
    limit: int,
) -> AssociationTableResults:
    total = query_result.response.num_found
    associations: List[DirectionalAssociation] = []
    for doc in query_result.response.docs:
        try:
            direction = get_association_direction(entity, doc)
            association = DirectionalAssociation(**doc, direction=direction)
            association.provided_by_link = (
                get_provided_by_link(association.provided_by) if association.provided_by else []
            )
            association.has_evidence_links = (
                get_links_for_field(association.has_evidence) if association.has_evidence else []
            )
            association.publications_links = (
                get_links_for_field(association.publications) if association.publications else []
            )
            associations.append(association)
        except ValidationError:
            logger.error(f"Validation error for {doc}")
            raise
    results = AssociationTableResults(
        items=associations,
        limit=limit,
        offset=offset,
        total=total,
        facet_fields=convert_facet_fields(query_result.facet_counts.facet_fields),
        facet_queries=convert_facet_queries(query_result.facet_counts.facet_queries),
    )
    for item, doc in zip(results.items, query_result.response.docs):
        if item.subject != doc["subject"]:
            raise ValueError(
                f"Parsed association subject {item.subject} does not match document subject {doc['subject']}"
            )
    return results


def parse_histopheno(query_result: SolrQueryResult, subject_closure: str) -> HistoPheno:
    """Parse a SolrQueryResult into a HistoPheno object"""
    bins = []
    for k, v in query_result.facet_counts.facet_queries.items():
        id = f"{k.split(':')[1]}:{k.split(':')[2]}".replace('"', "")
        label = HistoPhenoKeys(id).name
        bins.append(HistoBin(id=id, label=label, count=v))
    bins = sorted(bins, key=lambda x: x.count, reverse=True)

    return HistoPheno(id=subject_closure, items=bins)


def parse_search(
    query_result: SolrQueryResult,
    offset: int = 0,
    limit: int = 20,
) -> SearchResults:
    items = []
    for doc in query_result.response.docs:
        try:
            result = SearchResult(**doc)
            items.append(result)
        except ValidationError:
            logger.error(f"Validation error for {doc}")
            raise
    total = query_result.response.num_found
    facet_fields = convert_facet_fields(query_result.facet_counts.facet_fields)
    facet_queries = convert_facet_queries(query_result.facet_counts.facet_queries)
    return SearchResults(
        limit=limit, offset=offset, total=total, items=items, facet_fields=facet_fields, facet_queries=facet_queries
    )


def parse_autocomplete(query_result: SolrQueryResult) -> SearchResults:
    total = query_result.response.num_found
    items = []
    for doc in query_result.response.docs:
        try:
            result = SearchResult(**doc)
            items.append(result)
        except ValidationError:
            logger.error(f"Validation error for {doc}")
            raise
    return SearchResults(limit=10, offset=0, total=total, items=items)


def parse_mappings(query_result: SolrQueryResult, offset: int = 0, limit: int = 20) -> MappingResults:
    total = query_result.response.num_found
    items = []
    for doc in query_result.response.docs:
        try:
            result = Mapping(**doc)
            items.append(result)
        except ValidationError:
            logger.error(f"Validation error for {doc}")
            raise
    return MappingResults(limit=limit, offset=offset, total=total, items=items)


##################
# Parser Helpers #
##################


def convert_facet_fields(solr_facet_fields: Dict) -> List[FacetField]:
    """Converts list of raw Solr facet fields FacetField instances"""
    facet_fields: List[FacetField] = []
    for field in solr_facet_fields:
        ff = FacetField(label=field)
        facet_list = solr_facet_fields[field]
        facet_dict = dict(zip(facet_list[::2], facet_list[1::2]))
        ff.facet_values = [FacetValue(label=k, count=v) for k, v in facet_dict.items()]
        facet_fields.append(ff)
    return facet_fields


def convert_facet_queries(solr_facet_queries: Dict[str, int]) -> List[FacetValue]:
    """Converts list of raw Solr facet queries to FacetValue instances"""
    return [FacetValue(label=k, count=v) for k, v in solr_facet_queries.items()]


def get_association_direction(entity: List[str], document: Dict) -> AssociationDirectionEnum:
    """Get the direction of an association based on the entity and the association document"""
    if document.get("subject") in entity or (
        document.get("subject_closure") and any(e in document.get("subject_closure") for e in entity)
    ):
        direction = AssociationDirectionEnum.outgoing
    elif document.get("object") in entity or (
        document.get("object_closure") and any(e in document.get("object_closure") for e in entity)
    ):
        direction = AssociationDirectionEnum.incoming
    elif document.get("disease_context_qualifier") in entity or (
        document.get("disease_context_qualifier_closure")
        and any(e in document.get("disease_context_qualifier_closure") for e in entity)
    ):
        # This is a special case for disease_context_qualifier, if an association between two other entities
        # only occurs within the context of a disease, we can treat it like an incoming association
        direction = AssociationDirectionEnum.incoming
    else:
        raise ValueError(f"Entity {entity} not found in association {document}")
    return direction
