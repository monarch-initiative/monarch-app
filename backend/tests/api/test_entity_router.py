from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response
from monarch_py.api.entity import router

client = TestClient(router)


def test_entity(node):
    with patch.object(
        client, "get", MagicMock(return_value=Response(200, json=node, headers={"content-type": "application/json"}))
    ) as mock_get:
        response = client.get("/MONDO:0019391")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == node


def test_association_table(association_table):
    with patch.object(
        client,
        "get",
        MagicMock(return_value=Response(200, json=association_table, headers={"content-type": "application/json"})),
    ) as mock_get:
        response = client.get("/MONDO:0019391/biolink:DiseaseToPhenotypicFeatureAssociation")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == association_table
