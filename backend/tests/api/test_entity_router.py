from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from monarch_py.api.entity import router
from monarch_py.datamodels.model import Node

client = TestClient(router)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_entity")
def test_entity(mock_get_entity, node):
    mock_get_entity.return_value = Node(**node)
    client.get("/MONDO:0019391")
    mock_get_entity.assert_called_with("MONDO:0019391", extra=True)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_association_table")
def test_association_table(mock_get_assoc_table):
    mock_get_assoc_table.return_value = MagicMock()
    client.get("/MONDO:0019391/biolink:DiseaseToPhenotypicFeatureAssociation")
    mock_get_assoc_table.assert_called_with(
        entity="MONDO:0019391",
        category="biolink:DiseaseToPhenotypicFeatureAssociation",
        q=None,
        sort=None,
        offset=0,
        limit=20,
    )
