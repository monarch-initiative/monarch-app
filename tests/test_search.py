import pytest
from unittest.mock import Mock

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_api.model import EntityResults
# from monarch_py.datamodels.model import AssociationResults, Entity
from monarch_api.search import search

@pytest.mark.parametrize(
    "q, category, taxon, offset, limit",
    [
        ("MONDO:012933", None, None, None, None)
    ],
)
def test_search(q, category, taxon, offset, limit):
    # q="*:*", category=None, taxon=None, offset=None, limit=None):
    """
    Test that search calls search from monarch_py
    """
    si = Mock(spec=SolrImplementation)
    response = si.search(
        q=q,
        category=category,
        taxon=taxon,
        offset=offset,
        limit=limit
    )
    assert response
