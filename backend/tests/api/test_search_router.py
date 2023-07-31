from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response
from monarch_py.api.search import router

client = TestClient(router)


def test_search(search):
    with patch.object(
        client, "get", MagicMock(return_value=Response(200, json=search, headers={"content-type": "application/json"}))
    ):
        response = client.get("/search?q=heart")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == search
