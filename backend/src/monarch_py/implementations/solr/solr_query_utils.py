from typing import List, Optional

from monarch_py.datamodels.solr import HistoPhenoKeys, SolrQuery
from monarch_py.datamodels.category_enums import AssociationPredicate
from monarch_py.utils.association_type_utils import AssociationTypeMappings, get_solr_query_fragment
from monarch_py.utils.utils import escape


def build_association_query(
    category: Optional[List[str]] = None,
    subject: Optional[List[str]] = None,
    subject_closure: Optional[str] = None,
    subject_category: Optional[List[str]] = None,
    subject_namespace: Optional[List[str]] = None,
    subject_taxon: Optional[List[str]] = None,
    predicate: Optional[List[str]] = None,
    object: Optional[List[str]] = None,
    object_closure: Optional[str] = None,
    object_category: Optional[List[str]] = None,
    object_namespace: Optional[List[str]] = None,
    object_taxon: Optional[List[str]] = None,
    entity: Optional[List[str]] = None,
    direct: bool = False,
    q: Optional[str] = None,
    sort: Optional[List[str]] = None,
    facet_fields: Optional[List[str]] = None,
    facet_queries: Optional[List[str]] = None,
    filter_queries: Optional[List[str]] = None,
    facet_mincount: int = 1,
    offset: int = 0,
    limit: int = 20,
) -> SolrQuery:

    entity_fields = ["subject", "object", "disease_context_qualifier"]
    """Populate a SolrQuery object with association filters"""
    query = SolrQuery(start=offset, rows=limit)
    query.add_field_filter_query("category", None if not category else [c for c in category])
    query.add_field_filter_query("predicate", None if not predicate else [p for p in predicate])
    query.add_field_filter_query("subject_closure", subject_closure)
    query.add_field_filter_query("subject_category", None if not subject_category else [c for c in subject_category])
    query.add_field_filter_query("subject_namespace", subject_namespace)
    query.add_field_filter_query("subject_taxon", subject_taxon)
    query.add_field_filter_query("object_closure", object_closure)
    query.add_field_filter_query("object_category", None if not object_category else [c for c in object_category])
    query.add_field_filter_query("object_namespace", object_namespace)
    query.add_field_filter_query("object_taxon", object_taxon)
    if subject:
        if direct:
            query.add_field_filter_query("subject", " OR ".join(subject))
        else:
            query.add_filter_query(" OR ".join([f'subject:"{s}" OR subject_closure:"{s}"' for s in subject]))
    if object:
        if direct:
            query.add_field_filter_query("object", " OR ".join(object))
        else:
            query.add_filter_query(" OR ".join([f'object:"{o}" OR object_closure:"{o}"' for o in object]))
    if entity:
        if direct:
            query.add_filter_query(" OR ".join([f'{field}:"{e}"' for e in entity for field in entity_fields]))
        else:
            query.add_filter_query(
                " OR ".join([f'{field}:"{e}" OR {field}_closure:"{e}"' for e in entity for field in entity_fields])
            )
    if q:
        # We don't yet have tokenization strategies for the association index, initially we'll limit searching to
        # the visible fields in an association table plus their ID equivalents and use a wildcard query for substring matching
        query.q = q
        query.def_type = "edismax"
        query.hl = True
        query.query_fields = association_search_query_fields()
    if sort:
        query.sort = ", ".join(sort)
    if facet_fields:
        query.facet_fields = facet_fields
    if facet_queries:
        query.facet_queries = facet_queries
    if filter_queries:
        query.filter_queries.extend(filter_queries)
    query.facet_mincount = facet_mincount
    return query


def build_association_table_query(
    entity: List[str],
    category: str,
    direct: bool = False,
    q: Optional[str] = None,
    facet_fields: List[str] = None,
    facet_queries: List[str] = None,
    filter_queries: List[str] = None,
    offset: int = 0,
    limit: int = 5,
    sort: List[str] = None,
) -> SolrQuery:
    if sort is None:
        sort = [
            "frequency_computed_sortable_float desc",
            "evidence_count desc",
            "subject_label asc",
            "predicate asc",
            "object_label asc",
            "primary_knowledge_source asc",
        ]

    query = build_association_query(
        entity=entity,
        category=[category],
        q=q,
        sort=sort,
        offset=offset,
        limit=limit,
        direct=direct,
        facet_fields=facet_fields,
        facet_queries=facet_queries,
        filter_queries=filter_queries,
    )
    return query


def build_association_counts_query(entity: str) -> SolrQuery:
    subject_query = f'AND (subject:"{entity}" OR subject_closure:"{entity}")'
    object_query = f'AND (object:"{entity}" OR object_closure:"{entity}" OR disease_context_qualifier:"{entity}" OR disease_context_qualifier_closure:"{entity}")'

    # Run the same facet_queries constrained to matches against either the subject or object
    # to know which kind of label will be needed in the UI to refer to the opposite side of the association
    facet_queries = []
    for field_query in [subject_query, object_query]:
        for agm in AssociationTypeMappings.get_mappings():
            association_type_query = get_solr_query_fragment(agm)
            facet_queries.append(f"({association_type_query}) {field_query}")
    query = build_association_query(entity=[entity], facet_queries=facet_queries)
    return query


def build_histopheno_query(subject: str) -> SolrQuery:
    query = build_association_query(
        subject=[subject],
        offset=0,
        limit=0,
    )
    hpkeys = [i for i in HistoPhenoKeys]
    query.facet_queries = [f'object_closure:"{(i.value)}"' for i in hpkeys]
    return query


def build_multi_entity_association_query(
    entity: str,
    counterpart_category: Optional[str] = None,
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
    highlighting: bool = False,
    sort: Optional[str] = None,
) -> SolrQuery:
    query = SolrQuery(start=offset, rows=limit, sort=sort)
    query.q = q
    query.def_type = "edismax"
    query.query_fields = entity_query_fields()
    query.hl = highlighting
    query.boost = entity_boost(empty_search=(q == "*:*"))
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


def build_autocomplete_query(
    q: str, category: List[str] = None, prioritized_predicates: List[AssociationPredicate] = None
) -> SolrQuery:
    query = SolrQuery(q=q, rows=10, start=0)
    query.q = q
    if category:
        query.add_filter_query(" OR ".join(f'category:"{cat}"' for cat in category))
    # match the query fields to start with
    query.query_fields = entity_query_fields()
    query.def_type = "edismax"
    query.boost = entity_boost(prioritized_predicates=prioritized_predicates, empty_search=(q == "*:*"))
    return query


def build_mapping_query(
    entity_id: Optional[List[str]] = None,
    subject_id: Optional[List[str]] = None,
    predicate_id: Optional[List[str]] = None,
    object_id: Optional[List[str]] = None,
    mapping_justification: Optional[List[str]] = None,
    offset: int = 0,
    limit: int = 20,
) -> SolrQuery:
    query = SolrQuery(start=offset, rows=limit)
    if entity_id:
        query.add_filter_query(" OR ".join([f'subject_id:"{escape(i)}" OR object_id:"{escape(i)}"' for i in entity_id]))
    if subject_id:
        query.add_filter_query(" OR ".join([f'subject_id:"{escape(i)}"' for i in subject_id]))
    if predicate_id:
        query.add_filter_query(" OR ".join([f'predicate_id:"{escape(i)}"' for i in predicate_id]))
    if object_id:
        query.add_filter_query(" OR ".join([f'object_id:"{escape(i)}"' for i in object_id]))
    if mapping_justification:
        query.add_filter_query(" OR ".join([f'mapping_justification:"{escape(i)}"' for i in mapping_justification]))
    return query


def build_grounding_query(text: str) -> SolrQuery:
    query = SolrQuery(q=text, rows=10, start=0)
    query.q = f'"{text}"'  # quoting so that the complete text is matched as a unit
    # rather than _t (text) or _ac (autocomplete/starts-with), just use keyword fields
    query.query_fields = (
        "id^100 name^10 symbol^10 synonym name_grounding full_name_grounding symbol_grounding synonym_grounding"
    )
    query.def_type = "edismax"
    query.boost = obsolete_unboost(multiplier=0.001)
    return query


### Search helper functions ###


def obsolete_unboost(multiplier=0.1):
    return f'if(termfreq(deprecated,"true"),{multiplier},1)'


def entity_boost(prioritized_predicates: List[AssociationPredicate] = None, empty_search: bool = False) -> str:
    """Shared boost function between search and autocomplete"""
    phenotype_boost = category_boost("biolink:PhenotypicFeature", 1.1)
    disease_boost = category_boost("biolink:Disease", 1.3)
    human_gene_boost = category_boost("biolink:Gene", 1.1, taxon="NCBITaxon:9606")

    boosts = [phenotype_boost, disease_boost, human_gene_boost, obsolete_unboost()]
    if prioritized_predicates:
        boosts.append(entity_predicate_boost(prioritized_predicates, 2.0))
    if empty_search:
        boosts.append(blank_search_boost())
    return f"product({','.join(boosts)})"


def entity_predicate_boost(prioritized_predicates: List[AssociationPredicate], multiplier: float) -> str:
    boosts = []
    for predicate in prioritized_predicates:
        field_root = predicate.value.replace("biolink:", "")
        count_field = field_root + "_count"
        boosts.append(f"if({count_field},{multiplier},1)")
    return ",".join(boosts)


def category_boost(category: str, multiplier: float, taxon: Optional[str] = None) -> str:
    if taxon:
        return f'if(and(termfreq(in_taxon,"{taxon}"),termfreq(category,"{category}")),{multiplier},1)'
    else:
        return f'if(termfreq(category,"{category}"),{multiplier},1)'


def blank_search_boost() -> str:
    """
    Boost specific nodes that we'd like to see as site examples to the top for empty searches
    """
    example_nodes = [
        "MONDO:0007523",  # Ehlers-Danlos syndrome, hypermobility type
        "MONDO:0019391",  # Fanconi anemia
        "MONDO:0018954",  # Loeys-Dietz syndrome
        "MONDO:0011518",  # Wiedemann-Steiner syndrome
        "HP:0001166",  # Arachnodactyly
        "HP:0001631",  # Atrial septal defect
        "UBERON:0000948",  # heart
        "UBERON:0006585",  # vestibular organ
        "HGNC:4851",  # HTT
        "HGNC:3603",  # FBN1
    ]
    # boost score by 1.5 + i/10 for these nodes
    boosts = [f'if(termfreq(id,"{node}"),{len(example_nodes) - i + 2},1)' for i, node in enumerate(example_nodes)]
    boost = ",".join(boosts)
    return f"product({boost})"


def autocomplete_query_fields():
    """
    Fields and boosts used for autocomplete
    """
    return "id^100 name^10 name_t^5 name_ac symbol^10 symbol_t^5 symbol_ac synonym synonym_t synonym_ac"


def entity_query_fields():
    """
    Fields and boosts used for entity search, includes autocomplete fields and expands upon them beyond pure name fields
    """
    return f"{autocomplete_query_fields()} description_t xref"


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
