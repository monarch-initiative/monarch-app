import pytest

# from monarch_py.datamodels.solr import SolrQuery
from monarch_py.implementations.solr.solr_query_utils import build_association_query, build_histopheno_query
from monarch_py.utils.utils import dict_diff


def test_build_histopheno_query(histopheno_query):
    """Test the build_histopheno_query function"""
    query = build_histopheno_query("MONDO:0020121").dict()
    expected = histopheno_query
    assert (
        all([k in query for k in expected]) and 
        all([query[k] == expected[k] for k in expected])
    ), f"Query is not as expected. Difference: {dict_diff(query, expected)}"


@pytest.mark.parametrize(
    "direct",
    [
        True,
        False,
    ]
)
def test_build_association_query(
    direct,
    association_query_params,
    association_query_direct,
    association_query_indirect
    ):
    """Test the build_association_query function"""
    query = build_association_query(**association_query_params, direct=direct).dict()
    expected = association_query_direct if direct else association_query_indirect
    assert (
        all([k in query for k in expected]) and
        all([query[k] == expected[k] for k in expected])
    ), f"Query is not as expected. Difference: {dict_diff(query, expected)}"

