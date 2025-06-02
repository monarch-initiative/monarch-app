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
