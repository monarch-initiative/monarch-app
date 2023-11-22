from typing import List

from monarch_py.datamodels.solr import HistoPhenoKeys, SolrQuery
from monarch_py.utils.association_type_utils import AssociationTypeMappings, get_solr_query_fragment
from monarch_py.utils.utils import escape


def build_association_query(
    category: List[str] = None,
    predicate: List[str] = None,
    subject: List[str] = None,
    object: List[str] = None,
    subject_closure: str = None,
    object_closure: str = None,
    entity: List[str] = None,
    direct: bool = None,
    q: str = None,
    sort: List[str] = None,
    facet_fields: List[str] = None,
    facet_queries: List[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> SolrQuery:
    """Populate a SolrQuery object with association filters"""
    query = SolrQuery(start=offset, rows=limit)
    if category:
        query.add_filter_query(" OR ".join([f"category:{escape(cat)}" for cat in category]))
    if predicate:
        query.add_filter_query(" OR ".join([f"predicate:{escape(pred)}" for pred in predicate]))
    if subject:
        if direct:
            query.add_field_filter_query("subject", " OR ".join(subject))
        else:
            query.add_filter_query(" OR ".join([f'subject:"{s}" OR subject_closure:"{s}"' for s in subject]))
    if subject_closure:
        query.add_field_filter_query("subject_closure", subject_closure)
    if object:
        if direct:
            query.add_field_filter_query("object", " OR ".join(object))
        else:
            query.add_filter_query(" OR ".join([f'object:"{o}" OR object_closure:"{o}"' for o in object]))
    if object_closure:
        query.add_field_filter_query("object_closure", object_closure)
    if entity:
        if direct:
            query.add_filter_query(" OR ".join([f'subject:"{escape(e)}" OR object:"{escape(e)}"' for e in entity]))
        else:
            query.add_filter_query(
                " OR ".join(
                    [
                        f'subject:"{escape(e)}" OR subject_closure:"{escape(e)}" OR object:"{escape(e)}" OR object_closure:"{escape(e)}"'
                        for e in entity
                    ]
                )
            )
    if q:
        # We don't yet have tokenization strategies for the association index, initially we'll limit searching to
        # the visible fields in an association table plus their ID equivalents and use a wildcard query for substring matching
        query.q = q
        query.def_type = "edismax"
        query.query_fields = association_search_query_fields()
    if sort:
        query.sort = ", ".join(sort)
    if facet_fields:
        query.facet_fields = facet_fields
    if facet_queries:
        query.facet_queries = facet_queries
    return query


def build_association_table_query(
    entity: str, category: str, q: str = None, offset: int = 0, limit: int = 5, sort: List[str] = None
) -> SolrQuery:
    if sort is None:
        sort = [
            "evidence_count desc",
            "subject_label asc",
            "predicate asc",
            "object_label asc",
            "primary_knowledge_source asc",
        ]

    query = build_association_query(
        entity=[entity],
        category=[category],
        q=q,
        sort=sort,
        offset=offset,
        limit=limit,
    )
    return query


def build_association_counts_query(entity: str) -> SolrQuery:
    subject_query = f'AND (subject:"{entity}" OR subject_closure:"{entity}")'
    object_query = f'AND (object:"{entity}" OR object_closure:"{entity}")'
    # Run the same facet_queries constrained to matches against either the subject or object
    # to know which kind of label will be needed in the UI to refer to the opposite side of the association
    facet_queries = []
    for field_query in [subject_query, object_query]:
        for agm in AssociationTypeMappings.get_mappings():
            association_type_query = get_solr_query_fragment(agm)
            facet_queries.append(f"({association_type_query}) {field_query}")
    query = build_association_query(entity=[entity], facet_queries=facet_queries)
    return query


def build_histopheno_query(subject_closure: str) -> SolrQuery:
    query = build_association_query(
        subject_closure=subject_closure,
        offset=0,
        limit=0,
    )
    hpkeys = [i.value for i in HistoPhenoKeys]
    query.facet_queries = [f'object_closure:"{i}"' for i in hpkeys]
    return query


def build_multi_entity_association_query(
    entity: str,
    counterpart_category: str = None,
    # predicate: List[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> SolrQuery:
    """Populate a SolrQuery object with association filters"""
    query = SolrQuery(start=offset, rows=limit)
    if counterpart_category:
        query.add_filter_query(
            f'(subject:"{escape(entity)}" AND object_category:"{escape(counterpart_category)}") OR (object:"{escape(entity)}" AND subject_category:"{escape(counterpart_category)}")'
        )
    else:
        query.add_filter_query(f'(subject:"{escape(entity)}") OR (object:"{escape(entity)}")')
    return query


def build_search_query(
    q: str = "*:*",
    offset: int = 0,
    limit: int = 20,
    category: List[str] = None,
    in_taxon_label: List[str] = None,
    facet_fields: List[str] = None,
    facet_queries: List[str] = None,
    filter_queries: List[str] = None,
    sort: str = None,
) -> SolrQuery:
    query = SolrQuery(start=offset, rows=limit, sort=sort)
    query.q = q
    query.def_type = "edismax"
    query.query_fields = entity_query_fields()
    query.boost = entity_boost()
    if category:
        query.add_filter_query(" OR ".join(f'category:"{cat}"' for cat in category))
    if in_taxon_label:
        query.add_filter_query(" OR ".join([f'in_taxon_label:"{t}"' for t in in_taxon_label]))
    if facet_fields:
        query.facet_fields = facet_fields
    if facet_queries:
        query.facet_queries = facet_queries
    if filter_queries:
        query.filter_queries.extend(filter_queries)
    # Filter out entities that don't have names (required field, but some don't have them)
    query.add_filter_query("name:*")
    return query


def build_autocomplete_query(q: str) -> SolrQuery:
    query = SolrQuery(q=q, limit=10, start=0)
    query.q = q
    # match the query fields to start with
    query.query_fields = entity_query_fields()
    query.def_type = "edismax"
    query.boost = entity_boost()
    return query


def build_mapping_query(
    entity_id: List[str] = None,
    subject_id: List[str] = None,
    predicate_id: List[str] = None,
    object_id: List[str] = None,
    mapping_justification: List[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> SolrQuery:
    query = SolrQuery(start=offset, rows=limit)
    if entity_id:
        query.add_filter_query(" OR ".join([f'subject_id:"{escape(e)}" OR object_id:"{escape(e)}"' for e in entity_id]))
    if subject_id:
        query.add_filter_query(" OR ".join([f'subject_id:"{escape(e)}"' for e in subject_id]))
    if predicate_id:
        query.add_filter_query(" OR ".join([f'predicate_id:"{escape(e)}"' for e in predicate_id]))
    if object_id:
        query.add_filter_query(" OR ".join([f'object_id:"{escape(e)}"' for e in object_id]))
    if mapping_justification:
        query.add_filter_query(" OR ".join([f'mapping_justification:"{escape(e)}"' for e in mapping_justification]))
    return query


### Search helper functions ###


def entity_boost():
    """Shared boost function between search and autocomplete"""
    disease_boost = 'if(termfreq(category,"biolink:Disease"),10.0,1)'
    human_gene_boost = 'if(and(termfreq(in_taxon,"NCBITaxon:9606"),termfreq(category,"biolink:Gene")),5.0,1)'
    obsolete_unboost = 'if(termfreq(deprecated,"true"),0.1,1)'
    return f"product({disease_boost},{human_gene_boost},{obsolete_unboost})"


def entity_query_fields():
    """
    Shared query field list between search and autocomplete,
    since the field list and boosts are currently the same
    """
    return "id^100 name^10 name_t^5 name_ac symbol^10 symbol_t^5 symbol_ac synonym synonym_t synonym_ac"


def association_search_query_fields():
    """
    Shared field list for free text search on associations (e.g. for the association table)
    """

    return (
        "subject subject_label^2 subject_label_t subject_closure subject_closure_label subject_closure_label_t"
        " predicate predicate_t"
        " object object_label^2 object_label_t object_closure object_closure_label object_closure_label_t"
        " publications has_evidence primary_knowledge_source aggregator_knowledge_source provided_by "
    )
