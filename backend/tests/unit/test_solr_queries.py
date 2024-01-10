import pytest
from monarch_py.datamodels.model import Node
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_counts_query,
    build_association_query,
    build_autocomplete_query,
    build_histopheno_query,
    build_mapping_query,
    build_search_query,
)
from monarch_py.utils.utils import compare_dicts, dict_diff


@pytest.mark.parametrize(
    "direct, facet_fields, facet_queries",
    [
        (True, None, None),
        (False, None, None),
        (None, ["category", "predicate"], ["category:DiseaseToPhenotypicFeatureAssociation"]),
        (None, ["category", "predicate"], ["category:DiseaseToPhenotypicFeatureAssociation"]),
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
    query = build_association_query(category=["biolink:Disease", "biolink:PhenotypicFeature"])
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    category_filter = [fq for fq in query.filter_queries if fq.startswith("category:")][0]
    assert (
        category_filter == "category:biolink\\:Disease OR category:biolink\\:PhenotypicFeature"
    ), "multiple category filter is not as expected"


def test_build_association_multiple_predicates():
    query = build_association_query(predicate=["biolink:has_phenotype", "biolink:expressed_in"])
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    predicate_filter = [fq for fq in query.filter_queries if fq.startswith("predicate:")][0]
    assert (
        predicate_filter == "predicate:biolink\\:has_phenotype OR predicate:biolink\\:expressed_in"
    ), "multiple predicate filter is not as expected"


def test_build_association_multiple_entites():
    query = build_association_query(entity=["MONDO:0020121", "HP:0000006"])
    assert len(query.filter_queries) > 0, "filter_queries is empty"
    entity_filter = [fq for fq in query.filter_queries if fq.startswith("subject:")][0]
    assert (
        entity_filter
        == 'subject:"MONDO\\:0020121" OR subject_closure:"MONDO\\:0020121" OR object:"MONDO\\:0020121" OR object_closure:"MONDO\\:0020121" OR subject:"HP\\:0000006" OR subject_closure:"HP\\:0000006" OR object:"HP\\:0000006" OR object_closure:"HP\\:0000006"'
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
