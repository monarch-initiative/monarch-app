import urllib
from unittest.mock import MagicMock, patch

import pytest
from fastapi.exceptions import RequestValidationError

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
    search_params = {
        **params,
        "in_taxon": None,
        "subset": None,
        "exclude_subset": None,
        "facet_fields": ["category", "in_taxon_label"],
        "highlighting": True,
        "exact": False,
    }
    search_params["category"] = [EntityCategory(c) for c in search_params["category"]]
    search_params["category"] = [EntityCategory.DISEASE, EntityCategory.PHENOTYPIC_FEATURE]
    mock_search.assert_called_with(**search_params)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.search")
def test_search_grounding_params(mock_search, search):
    """The grounding-oriented params reach the implementation as typed values."""
    mock_search.return_value = SearchResults(**search)
    params = {
        "q": "septic shock",
        "match_type": "exact",
        "subset": ["rare"],
        "exclude_subset": ["venom_*"],
        "in_taxon": ["NCBITaxon:9606"],
    }
    client.get(f"/search?{urllib.parse.urlencode(params, doseq=True)}")
    kwargs = mock_search.call_args.kwargs
    assert kwargs["exact"] is True
    assert kwargs["subset"] == ["rare"]
    assert kwargs["exclude_subset"] == ["venom_*"]
    assert kwargs["in_taxon"] == ["NCBITaxon:9606"]


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.search")
def test_search_defaults_to_relevance(mock_search, search):
    """Omitting match_type keeps the recall-oriented search contract."""
    mock_search.return_value = SearchResults(**search)
    client.get("/search?q=septic+shock")
    assert mock_search.call_args.kwargs["exact"] is False


def test_search_rejects_unknown_match_type():
    """match_type is a closed enum, so a typo fails validation rather than silently
    falling back to relevance. TestClient is built on the bare router here, which has no
    exception handler mounted, so the validation error surfaces as a raise rather than
    the 422 the mounted app would return."""
    with pytest.raises(RequestValidationError) as excinfo:
        client.get("/search?q=heart&match_type=fuzzy")
    assert excinfo.value.errors()[0]["loc"] == ("query", "match_type")


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.autocomplete")
def test_autocomplete_params(mock_autocomplete, autocomplete):
    mock_autocomplete.return_value = autocomplete
    client.get(f"/autocomplete?q=heart")
    mock_autocomplete.assert_called_with(q="heart")
