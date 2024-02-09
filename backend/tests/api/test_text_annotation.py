from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from monarch_py.api.text_annotation import router

client = TestClient(router)


@patch("monarch_py.implementations.spacy.spacy_implementation.SpacyImplementation.annotate_text")
def test_get_annotate(mock_annotate):
    mock_annotate.return_value = '<span class="this-is-just-mocked">Ehlers-Danlos syndrome</span>'
    response = client.get("/annotate?text=Ehlers-Danlos syndrome")
    assert response.status_code == 200
    mock_annotate.assert_called_with("Ehlers-Danlos syndrome")


@patch("monarch_py.implementations.spacy.spacy_implementation.SpacyImplementation.annotate_text")
def test_post_annotate(mock_annotate):
    mock_annotate.return_value = '<span class="this-is-just-mocked">Ehlers-Danlos syndrome</span>'
    response = client.post("/annotate", json={"content": "Ehlers-Danlos syndrome"})
    assert response.status_code == 200
    mock_annotate.assert_called_with("Ehlers-Danlos syndrome")


@patch("monarch_py.implementations.spacy.spacy_implementation.SpacyImplementation.get_annotated_entities")
def test_get_annotate_entities(mock_annotate):
    mock_annotate.return_value = MagicMock()
    response = client.get("/annotate/entities?text=Ehlers-Danlos syndrome")
    assert response.status_code == 200
    mock_annotate.assert_called_with("Ehlers-Danlos syndrome")


@patch("monarch_py.implementations.spacy.spacy_implementation.SpacyImplementation.get_annotated_entities")
def test_post_annotate_entities(mock_annotate):
    mock_annotate.return_value = MagicMock()
    response = client.post("/annotate/entities", json={"content": "Ehlers-Danlos syndrome"})
    assert response.status_code == 200
    mock_annotate.assert_called_with("Ehlers-Danlos syndrome")
