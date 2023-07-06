from unittest.mock import Mock

import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation


@pytest.mark.parametrize(
    "q, category, taxon, offset, limit",
    [("MONDO:012933", None, None, None, None)],
)
def test_search(q, category, taxon, offset, limit):
    """
    Test that search calls search from monarch_py
    """
    si = Mock(spec=SolrImplementation)
    response = si.search(q=q, category=category, taxon=taxon, offset=offset, limit=limit)
    assert response
