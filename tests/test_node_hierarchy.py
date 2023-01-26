# write a test that uses mocking to test the get_node_hierarchy function
from monarch_api.model import Entity
from monarch_api.utils.entity_utils import get_node_hierarchy
import pytest
from unittest.mock import Mock
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import Association, Entity, AssociationResults


def test_get_node_hierarchy():
    """
    Test that get_node_hierarchy calls get_associations from monarch_py
    """

    # create a mock solr implementation
    si = Mock(spec=SolrImplementation, get_associations=Mock(return_value=AssociationResults()))

    # call get_node_hierarchy and assert that it calls get_associations
    get_node_hierarchy(Entity(id="MONDO:0007947"), si)

    # Assert that get_associations was called three times
    assert si.get_associations.call_count == 3
