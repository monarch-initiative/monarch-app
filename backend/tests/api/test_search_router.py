import urllib
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response

from monarch_py.api.search import router
from monarch_py.datamodels.category_enums import EntityCategory
from monarch_py.datamodels.model import SearchResults

client = TestClient(router)


def test_search(search):
    with patch.object(
        client, "get", MagicMock(return_value=Response(200, json=search, headers={"content-type": "application/json"}))
    ):
        response = client.get("/search?q=heart")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == search


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.search")
def test_search_params(mock_search, search):
    mock_search.return_value = SearchResults(**search)
    params = {
        "q": "heart",
        "category": [EntityCategory.DISEASE.value, EntityCategory.PHENOTYPIC_FEATURE.value],
        "in_taxon_label": ["NCBITaxon:9606", "NCBITaxon:10090"],
        "offset": 0,
        "limit": 20,
    }

    query_string = urllib.parse.urlencode(params, doseq=True)
    client.get(f"/search?{query_string}")
    search_params = {**params, "facet_fields": ["category", "in_taxon_label"], "highlighting": True}
    search_params["category"] = [EntityCategory(c) for c in search_params["category"]]
    search_params["category"] = [EntityCategory.DISEASE, EntityCategory.PHENOTYPIC_FEATURE]
    mock_search.assert_called_with(**search_params)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.autocomplete")
def test_autocomplete_params(mock_autocomplete, autocomplete):
    mock_autocomplete.return_value = autocomplete
    client.get(f"/autocomplete?q=heart")
    mock_autocomplete.assert_called_with(q="heart")
