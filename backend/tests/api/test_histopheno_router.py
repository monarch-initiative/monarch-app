from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response

from monarch_py.api.histopheno import router
from monarch_py.datamodels.model import HistoPheno

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


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_histopheno")
def test_histopheno_params(mock_get_histopheno, histopheno):
    mock_get_histopheno.return_value = HistoPheno(**histopheno)
    client.get("/HP:0000001")
    mock_get_histopheno.assert_called_with("HP:0000001")
