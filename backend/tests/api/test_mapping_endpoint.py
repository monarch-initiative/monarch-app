from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response
from monarch_py.api.search import router

client = TestClient(router)


def test_mappings(search):
    with patch.object(
        client, "get", MagicMock(return_value=Response(200, json=search, headers={"content-type": "application/json"}))
    ):
        response = client.get("/mappings?entity_id=MONDO:0000015")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == search

