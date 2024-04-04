import urllib
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response

from monarch_py.api.search import router
from monarch_py.datamodels.category_enums import MappingPredicate
from monarch_py.datamodels.model import MappingResults

client = TestClient(router)


def test_mappings(search):
    with patch.object(
        client, "get", MagicMock(return_value=Response(200, json=search, headers={"content-type": "application/json"}))
    ):
        response = client.get("/mappings?entity_id=MONDO:0000015")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == search


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_mappings")
def test_mappings_params(mock_get_mappings, mappings):
    mock_get_mappings.return_value = MagicMock()
    params = {
        "entity_id": ["MONDO:0000015", "MONDO:0000016"],
        "subject_id": ["HGNC:0000001", "HGNC:0000002"],
        "predicate_id": ["skos:exactMatch"],
        "object_id": ["MONDO:0000001", "MONDO:0000002"],
        "mapping_justification": ["semapv:UnspecifiedMatching"],
        "offset": 0,
        "limit": 20,
    }
    query_string = urllib.parse.urlencode(params, doseq=True)
    mappings = MappingResults(**mappings)
    client.get(f"/mappings?{query_string}")
    mock_get_mappings.assert_called_with(
        entity_id=["MONDO:0000015", "MONDO:0000016"],
        subject_id=["HGNC:0000001", "HGNC:0000002"],
        predicate_id=[MappingPredicate.EXACT_MATCH],
        object_id=["MONDO:0000001", "MONDO:0000002"],
        mapping_justification=["semapv:UnspecifiedMatching"],
        offset=0,
        limit=20,
    )
