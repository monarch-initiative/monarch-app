from typing import Dict, List

from loguru import logger
from pydantic import ValidationError

from monarch_py.datamodels.model import (
    Association,
    AssociationCount,
    AssociationCountList,
    AssociationDirectionEnum,
    AssociationResults,
    AssociationTableResults,
    CounterpartAssociation,
    DirectionalAssociation,
    Entity,
    FacetField,
    FacetValue,
    HistoBin,
    HistoPheno,
    SearchResult,
    SearchResults,
    ExpandedCurie
)
from monarch_py.datamodels.solr import HistoPhenoKeys, SolrQueryResult
from monarch_py.utils.association_type_utils import get_association_type_mapping_by_query_string
from monarch_py.utils.utils import get_links_for_field, get_provided_by_link

####################
# Parser functions #
####################


def parse_associations(
    query_result: SolrQueryResult,
    offset: int = 0,
    limit: int = 20,
) -> AssociationResults:
    associations = []
    for doc in query_result.response.docs:
        try:
            association = Association(**doc)
        except ValidationError:
            logger.error(f"Validation error for {doc}")
            raise ValidationError
        association.provided_by_link = get_provided_by_link(association.provided_by) if association.provided_by else None
        association.has_evidence_links = (
            get_links_for_field(association.has_evidence) if association.has_evidence else []
        )
        association.publications_links = (
            get_links_for_field(association.publications) if association.publications else []
        )
        associations.append(association)
    total = query_result.response.num_found
    return AssociationResults(items=associations, limit=limit, offset=offset, total=total)


def parse_association_counts(query_result: SolrQueryResult, entity: str) -> AssociationCountList:
    subject_query = f'AND (subject:"{entity}" OR subject_closure:"{entity}")'
    object_query = f'AND (object:"{entity}" OR object_closure:"{entity}")'
    association_count_dict: Dict[str, AssociationCount] = {}
    for k, v in query_result.facet_counts.facet_queries.items():
        if v > 0:
            if k.endswith(subject_query):
                original_query = k.replace(f" {subject_query}", "").lstrip("(").rstrip(")")
                agm = get_association_type_mapping_by_query_string(original_query)
                label = agm.object_label
            elif k.endswith(object_query):
                original_query = k.replace(f" {object_query}", "").lstrip("(").rstrip(")")
                agm = get_association_type_mapping_by_query_string(original_query)
                label = agm.subject_label
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


def parse_counterpart_associations(query_result: SolrQueryResult, entity: str) -> (dict, List[CounterpartAssociation]):
    associations = []
    this_entity = {
        "original_entity": None,
        "entity_namespace": None,
        "entity_category": None,
        "entity_closure": None,
        "entity_closure_label": None,
        "entity_taxon": None,
        "entity_taxon_label": None,
    }
    for doc in query_result.response.docs:
        try:
            association = Association(**doc)
        except ValidationError:
            logger.error(f"Validation error for {doc}")
            raise ValidationError
        provided_by_link = get_provided_by_link(association.provided_by) if association.provided_by else None
        if association.subject == entity or entity in association.subject_closure:
            this_entity = {
                "original_entity": association.original_subject,
                "entity_namespace": association.subject_namespace,
                "entity_category": association.subject_category,
                "entity_closure": association.subject_closure,
                "entity_closure_label": association.subject_closure_label,
                "entity_taxon": association.subject_taxon,
                "entity_taxon_label": association.subject_taxon_label,
            }
            counterpart_id = association.object
            original_counterpart = association.original_object
            counterpart_namespace = association.object_namespace
            counterpart_category = association.object_category
            counterpart_closure = association.object_closure
            counterpart_label = association.object_label
            counterpart_closure_label = association.object_closure_label
            counterpart_taxon = association.object_taxon
            counterpart_taxon_label = association.object_taxon_label
        elif association.object == entity or entity in association.object_closure:
            this_entity = {
                "original_entity": association.original_object,
                "entity_namespace": association.object_namespace,
                "entity_category": association.object_category,
                "entity_closure": association.object_closure,
                "entity_closure_label": association.object_closure_label,
                "entity_taxon": association.object_taxon,
                "entity_taxon_label": association.object_taxon_label,
            }
            counterpart_id = association.subject
            original_counterpart = association.original_subject
            counterpart_namespace = association.subject_namespace
            counterpart_category = association.subject_category
            counterpart_closure = association.subject_closure
            counterpart_label = association.subject_label
            counterpart_closure_label = association.subject_closure_label
            counterpart_taxon = association.subject_taxon
            counterpart_taxon_label = association.subject_taxon_label
        else:
            raise ValueError(f"Entity {entity} not found in association {association}")

        counterpart_association = CounterpartAssociation(
            id=association.id,
            category=association.category,
            counterpart_id=counterpart_id,
            original_counterpart=original_counterpart,
            counterpart_namespace=counterpart_namespace,
            counterpart_category=counterpart_category,
            counterpart_closure=counterpart_closure,
            counterpart_label=counterpart_label,
            counterpart_closure_label=counterpart_closure_label,
            counterpart_taxon=counterpart_taxon,
            counterpart_taxon_label=counterpart_taxon_label,
            predicate=association.predicate,
            primary_knowledge_source=association.primary_knowledge_source,
            aggregator_knowledge_source=association.aggregator_knowledge_source,
            negated=association.negated,
            pathway=association.pathway,
            provided_by=association.provided_by,
            provided_by_link=provided_by_link,
            publications=association.publications,
            qualifiers=association.qualifiers,
            has_evidence=association.has_evidence,
            evidence_count=association.evidence_count,
            frequency_qualifier=association.frequency_qualifier,
            onset_qualifier=association.onset_qualifier,
            sex_qualifier=association.sex_qualifier,
            stage_qualifier=association.stage_qualifier,
            frequency_qualifier_label=association.frequency_qualifier_label,
            frequency_qualifier_namespace=association.frequency_qualifier_namespace,
            frequency_qualifier_category=association.frequency_qualifier_category,
            frequency_qualifier_closure=association.frequency_qualifier_closure,
            frequency_qualifier_closure_label=association.frequency_qualifier_closure_label,
            onset_qualifier_label=association.onset_qualifier_label,
            onset_qualifier_namespace=association.onset_qualifier_namespace,
            onset_qualifier_category=association.onset_qualifier_category,
            onset_qualifier_closure=association.onset_qualifier_closure,
            onset_qualifier_closure_label=association.onset_qualifier_closure_label,
            sex_qualifier_label=association.sex_qualifier_label,
            sex_qualifier_namespace=association.sex_qualifier_namespace,
            sex_qualifier_category=association.sex_qualifier_category,
            sex_qualifier_closure=association.sex_qualifier_closure,
            sex_qualifier_closure_label=association.sex_qualifier_closure_label,
            stage_qualifier_label=association.stage_qualifier_label,
            stage_qualifier_namespace=association.stage_qualifier_namespace,
            stage_qualifier_category=association.stage_qualifier_category,
            stage_qualifier_closure=association.stage_qualifier_closure,
            stage_qualifier_closure_label=association.stage_qualifier_closure_label,
        )
        associations.append(counterpart_association)
    return (this_entity, associations)


def parse_entity(solr_document: Dict) -> Entity:
    try:
        entity = Entity(**solr_document)
    except ValidationError:
        logger.error(f"Validation error for {solr_document}")
        raise
    return entity


def parse_association_table(
    query_result: SolrQueryResult,
    entity: str,
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
    results = AssociationTableResults(items=associations, limit=limit, offset=offset, total=total)
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


def get_association_direction(entity: str, document: Dict) -> AssociationDirectionEnum:
    if document.get("subject") == entity or (
        document.get("subject_closure") and entity in document.get("subject_closure")
    ):
        direction = AssociationDirectionEnum.outgoing
    elif document.get("object") == entity or (
        document.get("object_closure") and entity in document.get("object_closure")
    ):
        direction = AssociationDirectionEnum.incoming
    else:
        raise ValueError(f"Entity {entity} not found in association {document}")
    return direction
