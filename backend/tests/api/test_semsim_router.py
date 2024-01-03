import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import MagicMock, patch

from monarch_py.api.additional_models import SemsimSearchGroup
from monarch_py.api.semsim import router

client = TestClient(router)


@pytest.mark.skip(reason="Not implemented")
def test_semsim(semsim):
    ...


@patch("monarch_py.api.semsim._search")
def test_get_search(mock_search):
    mock_search.return_value = ["Term1", "Term2"]

    termset = "HP:123, HP:456"
    group = "Human Genes"
    limit = 5

    response = client.get(f"/search/{termset}/{group}?limit={limit}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == ["Term1", "Term2"]
    mock_search.assert_called_once_with(termset=["HP:123", "HP:456"], prefix="Human Genes", limit=5)


@patch("monarch_py.api.config.SemsimianHTTPRequester.search")
def test_search(mock_search):
    mock_search.return_value = MagicMock()

    termset = "HP:123, HP:456"
    group = SemsimSearchGroup.HGNC
    limit = 5

    response = client.get(f"/search/{termset}/{group.value}?limit={limit}")

    assert response.status_code == status.HTTP_200_OK
    mock_search.assert_called_once_with(termset=["HP:123", "HP:456"], prefix=group.name, limit=limit)