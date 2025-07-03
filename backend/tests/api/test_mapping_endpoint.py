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


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_mappings")
def test_empty_response(mock_get_mappings):
    empty_mapping_result = MappingResults(items=[], offset=0, limit=20, total=0)
    mock_get_mappings.return_value = empty_mapping_result

    response = client.get("/mappings?entity_id=NONEXISTENT:ID")
    assert response.status_code == 200
    assert response.json() == {"items": [], "offset": 0, "limit": 20, "total": 0}
    assert response.text == '{"limit":20,"offset":0,"total":0,"items":[]}'
    mock_get_mappings.assert_called_once()


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_mappings")
def test_tsv_format(mock_get_mappings, mappings):
    mapping_res = MappingResults(**mappings)
    mock_get_mappings.return_value = mapping_res
    with patch("monarch_py.api.search.to_tsv") as mock_to_tsv:
        expected_result = "header1\theader2\nvalue1\tvalue2\n"
        mock_to_tsv.return_value = expected_result
        response = client.get("/mappings?entity_id=ANY:0000015&format=tsv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/tab-separated-values; charset=utf-8"
        assert response.text == expected_result
        mock_to_tsv.assert_called_with(mapping_res, print_output=False)
