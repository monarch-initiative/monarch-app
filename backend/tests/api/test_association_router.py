from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response
from monarch_py.api.association import router

client = TestClient(router)


def test_associations(associations):
    with patch.object(
        client,
        "get",
        MagicMock(return_value=Response(200, json=associations, headers={"content-type": "application/json"})),
    ) as mock_get:
        response = client.get("/association?subject=MONDO:0019391&object=HP:0000001")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == associations
