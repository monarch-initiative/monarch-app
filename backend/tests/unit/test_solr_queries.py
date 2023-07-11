import pytest
from monarch_py.datamodels.model import Node
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_counts_query,
    build_association_query,
    build_autocomplete_query,
    build_histopheno_query,
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
    ).dict()
    expected = association_query_direct if direct else association_query_indirect
    if facet_fields:
        expected["facet_fields"] = facet_fields
    if facet_queries:
        expected["facet_queries"] = facet_queries
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_association_counts_query(association_counts_query, node):
    query = build_association_counts_query(entity=Node(**node).id).dict()
    expected = association_counts_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_histopheno_query(histopheno_query):
    query = build_histopheno_query("MONDO:0020121").dict()
    expected = histopheno_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_search_query(search_query):
    query = build_search_query(q="fanconi").dict()
    expected = search_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


def test_build_autocomplete_query(autocomplete_query):
    query = build_autocomplete_query(q="fanc").dict()
    expected = autocomplete_query
    assert compare_dicts(query, expected), f"Query is not as expected. Difference: {dict_diff(query, expected)}"
