from typing import Any, Dict, List, Type, Union, get_args, get_origin, get_type_hints

from loguru import logger
from pydantic import BaseModel, ValidationError

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
from monarch_py.utils.association_type_utils import get_association_type_mapping_by_query_string
from monarch_py.utils.utils import get_links_for_field, get_provided_by_link


#############################
# Solr document normalizers #
#############################


def _is_scalar_type(type_hint: Any) -> bool:
    """
    Check if a type hint represents a scalar (non-list) type.

    Handles Optional[T], Union[T, None], and plain types.
    Returns True for str, int, bool, float, etc.
    Returns False for list[T], List[T], etc.
    """
    origin = get_origin(type_hint)

    # Handle Optional[T] which is Union[T, None]
    if origin is Union:
        args = get_args(type_hint)
        # Filter out NoneType and check remaining types
        non_none_args = [a for a in args if a is not type(None)]
        if len(non_none_args) == 1:
            return _is_scalar_type(non_none_args[0])
        return False

    # list, List[T] have origin of list
    if origin is list:
        return False

    # Plain types (str, int, bool, etc.) have no origin
    if origin is None:
        return type_hint in (str, int, float, bool)

    return False


def normalize_solr_doc_for_model(doc: Dict, model_class: Type[BaseModel]) -> Dict:
    """
    Normalize a Solr document to match Pydantic model field types.

    Solr often returns single values as lists when the field schema isn't
    pre-defined (dynamic fields default to multiValued). This converts
    single-element lists to scalars for fields that expect scalar types
    in the target Pydantic model.

    Args:
        doc: Raw Solr document dictionary
        model_class: Target Pydantic model class to normalize for

    Returns:
        Normalized document with list-to-scalar conversions applied
    """
    try:
        hints = get_type_hints(model_class)
    except Exception:
        # If we can't get type hints, return doc unchanged
        return doc

    normalized = dict(doc)

    for field_name, value in doc.items():
        if field_name not in hints:
            continue
        if not isinstance(value, list):
            continue

        field_type = hints[field_name]
        if _is_scalar_type(field_type):
            # Convert list to scalar: take first element or None
            normalized[field_name] = value[0] if value else None

    return normalized


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


def parse_association_counts(query_result: SolrQueryResult, entity: str) -> AssociationCountList:
    subject_query = f'AND (subject:"{entity}" OR subject_closure:"{entity}")'
    object_query = f'AND (object:"{entity}" OR object_closure:"{entity}" OR disease_context_qualifier:"{entity}" OR disease_context_qualifier_closure:"{entity}")'
    association_count_dict: Dict[str, AssociationCount] = {}
    for k, v in query_result.facet_counts.facet_queries.items():
        if v > 0:
            if k.endswith(subject_query):
                original_query = k.replace(f" {subject_query}", "").lstrip("(").rstrip(")")
                agm = get_association_type_mapping_by_query_string(original_query)
                label = agm.subject_label
            elif k.endswith(object_query):
                original_query = k.replace(f" {object_query}", "").lstrip("(").rstrip(")")
                agm = get_association_type_mapping_by_query_string(original_query)
                label = agm.object_label
                # always use forward for symmetric association types
            else:
                raise ValueError(f"Unexpected facet query when building association counts: {k}")
            # Symmetric associations need to be summed together, since both directions will be returned
            # when searching for associations by type
            if label in association_count_dict and agm.symmetric:
                association_count_dict[label].count += v
            else:
                association_count_dict[label] = AssociationCount(
                    label=label,
                    count=v,
                    category=agm.category,
                )
    return AssociationCountList(items=list(association_count_dict.values()))


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
    for i in zip(results.items, query_result.response.docs):
        assert i[0].subject == i[1]["subject"]
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
