import pytest

from monarch_py.datamodels.category_enums import (
    AssociationCategory,
    AssociationPredicate,
)
from monarch_py.datamodels.model import Node
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_counts_query,
    build_association_query,
    build_autocomplete_query,
    build_histopheno_query,
    build_mapping_query,
    build_search_query,
    obsolete_unboost,
    entity_predicate_boost,
    category_boost,
    blank_search_boost,
)
from monarch_py.utils.utils import compare_dicts, dict_diff


@pytest.mark.parametrize(
    "direct, facet_fields, facet_queries",
    [
        (True, None, None),
        (False, None, None),
        (None, ["category", "predicate"], [AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION.value]),
        (None, ["category", "predicate"], [AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION.value]),
    ],
)
def test_build_association_query(
    direct,
    facet_fields,
    facet_queries,
    association_query_params,
    association_query_direct,
    association_query_indirect,
):
    query = build_association_query(
        **association_query_params,
        direct=direct,
        facet_fields=facet_fields,
        facet_queries=facet_queries,
    ).model_dump()
    expected = association_query_direct if direct else association_query_indirect
    if facet_fields:
        expected["facet_fields"] = facet_fields
    if facet_queries:
        expected["facet_queries"] = facet_queries
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_association_multiple_categories():
    query = build_association_query(
        category=[
            AssociationCategory.CAUSAL_GENE_TO_DISEASE_ASSOCIATION.value,
            AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION.value,
        ]
    )
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    category_filter = [fq for fq in query.filter_queries if fq.startswith("category:")][0]
    assert (
        category_filter
        == "category:biolink\\:CausalGeneToDiseaseAssociation OR category:biolink\\:DiseaseToPhenotypicFeatureAssociation"
    ), "multiple category filter is not as expected"


def test_build_association_multiple_predicates():
    query = build_association_query(
        predicate=[AssociationPredicate.HAS_PHENOTYPE.value, AssociationPredicate.EXPRESSED_IN.value]
    )
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    predicate_filter = [fq for fq in query.filter_queries if fq.startswith("predicate:")][0]
    assert predicate_filter == "predicate:biolink\\:has_phenotype OR predicate:biolink\\:expressed_in", (
        "multiple predicate filter is not as expected"
    )


def test_build_association_multiple_entites():
    query = build_association_query(entity=["MONDO:0020121", "HP:0000006"])
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    entity_filter = [fq for fq in query.filter_queries if fq.startswith("subject:")][0]
    assert (
        entity_filter
        == 'subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121" OR object:"MONDO:0020121" OR object_closure:"MONDO:0020121" OR disease_context_qualifier:"MONDO:0020121" OR disease_context_qualifier_closure:"MONDO:0020121" OR subject:"HP:0000006" OR subject_closure:"HP:0000006" OR object:"HP:0000006" OR object_closure:"HP:0000006" OR disease_context_qualifier:"HP:0000006" OR disease_context_qualifier_closure:"HP:0000006"'
    )


def test_build_association_multiple_subjects():
    query = build_association_query(subject=["MONDO:0020121", "MONDO:0007915"])
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    subject_filter = [fq for fq in query.filter_queries if fq.startswith("subject:")][0]
    assert (
        subject_filter
        == 'subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121" OR subject:"MONDO:0007915" OR subject_closure:"MONDO:0007915"'
    ), "multiple subject filter is not as expected"


def test_build_association_multiple_objects():
    query = build_association_query(object=["HP:0000006", "HP:0000007"])
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    object_filter = [fq for fq in query.filter_queries if fq.startswith("object:")][0]
    print(object_filter)
    assert (
        object_filter
        == 'object:"HP:0000006" OR object_closure:"HP:0000006" OR object:"HP:0000007" OR object_closure:"HP:0000007"'
    ), "multiple object filter is not as expected"


def test_build_association_counts_query(association_counts_query, node):
    query = build_association_counts_query(entity=Node(**node).id).model_dump()
    expected = association_counts_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_histopheno_query(histopheno_query):
    query = build_histopheno_query("MONDO:0020121").model_dump()
    expected = histopheno_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_search_query(search_query):
    query = build_search_query(q="fanconi").model_dump()
    expected = search_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_autocomplete_query(autocomplete_query):
    query = build_autocomplete_query(q="fanc").model_dump()
    expected = autocomplete_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_mappings_query(mapping_query):
    query = build_mapping_query(entity_id=["MONDO:0020121"]).model_dump()
    expected = mapping_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_obsolete_unboost():
    boost = obsolete_unboost()
    assert "deprecated" in boost


def test_entity_predicate_boost() -> str:
    boost = entity_predicate_boost([AssociationPredicate.HAS_PHENOTYPE], 2.0)
    assert "has_phenotype_count" in boost
    assert "2.0" in boost


def test_category_boost():
    boost = category_boost("biolink:PhenotypicFeature", 99.0)
    assert "biolink:PhenotypicFeature" in boost
    assert "99.0" in boost


def test_category_boost_with_taxon():
    boost = category_boost("biolink:Gene", 100.0, taxon="NCBITaxon:9606")
    assert "biolink:Gene" in boost
    assert "100.0" in boost
    assert "NCBITaxon:9606" in boost


def test_blank_search_boost():
    boost = blank_search_boost()
    assert boost.startswith("product(")
    assert boost.endswith(")")
    assert 'if(termfreq(id,"MONDO:0007523"),12,1)' in boost
