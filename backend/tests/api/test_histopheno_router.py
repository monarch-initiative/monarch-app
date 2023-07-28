from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response
from monarch_py.api.histopheno import router

client = TestClient(router)


def test_histopheno(histopheno):
    with patch.object(
        client,
        "get",
        MagicMock(return_value=Response(200, json=histopheno, headers={"content-type": "application/json"})),
    ):
        response = client.get("/histopheno/HP:0000001")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == histopheno
