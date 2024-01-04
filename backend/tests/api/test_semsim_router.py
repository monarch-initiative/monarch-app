import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import MagicMock, patch

from monarch_py.api.additional_models import SemsimSearchGroup
from monarch_py.api.semsim import router

client = TestClient(router)


@patch("monarch_py.api.config.SemsimianHTTPRequester.compare")
def test_get_compare(mock_compare):
    mock_compare.return_value = MagicMock()

    subjects = "HP:123,HP:456"
    objects = "HP:789,HP:101112"

    response = client.get(f"/compare/{subjects}/{objects}")

    assert response.status_code == status.HTTP_200_OK
    mock_compare.assert_called_once_with(subjects=["HP:123", "HP:456"], objects=["HP:789", "HP:101112"])


@patch("monarch_py.api.config.SemsimianHTTPRequester.compare")
def test_post_compare(mock_compare):
    mock_compare.return_value = MagicMock()

    subjects = ["HP:123", "HP:456"]
    objects = ["HP:789", "HP:101112"]

    response = client.post(f"/compare/", json={"subjects": subjects, "objects": objects})

    assert response.status_code == status.HTTP_200_OK
    mock_compare.assert_called_once_with(subjects=subjects, objects=objects)


@patch("monarch_py.api.config.SemsimianHTTPRequester.search")
@pytest.mark.parametrize("termset", ["HP:123,HP:456", "HP:123, HP:456", " HP:123, HP:456 "])
def test_get_search(mock_search, termset: str):
    mock_search.return_value = MagicMock()

    group = SemsimSearchGroup.HGNC
    limit = 5

    response = client.get(f"/search/{termset}/{group.value}?limit={limit}")

    assert response.status_code == status.HTTP_200_OK
    mock_search.assert_called_once_with(termset=["HP:123", "HP:456"], prefix=group.name, limit=limit)


@patch("monarch_py.api.config.SemsimianHTTPRequester.search")
def test_post_search(mock_search):
    mock_search.return_value = MagicMock()

    termset = ["HP:123", "HP:456"]
    group = SemsimSearchGroup.HGNC
    limit = 5

    response = client.post(f"/search/", json={"termset": termset, "group": group.value, "limit": limit})

    assert response.status_code == status.HTTP_200_OK
    mock_search.assert_called_once_with(termset=["HP:123", "HP:456"], prefix=group.name, limit=limit)
