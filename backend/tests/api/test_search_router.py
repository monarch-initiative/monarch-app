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
        "namespace": None,
        "exclude_namespace": None,
        "subset": None,
        "exclude_subset": None,
        "scope": None,
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


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.search")
def test_search_scope_and_namespace_params(mock_search, search):
    mock_search.return_value = SearchResults(**search)
    params = {"q": "septic shock", "scope": "human_disease", "namespace": ["MONDO"], "exclude_namespace": ["MPATH"]}
    client.get(f"/search?{urllib.parse.urlencode(params, doseq=True)}")
    kwargs = mock_search.call_args.kwargs
    assert str(kwargs["scope"]) == "human_disease"
    assert kwargs["namespace"] == ["MONDO"]
    assert kwargs["exclude_namespace"] == ["MPATH"]


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.search")
def test_search_facet_fields_default_unchanged(mock_search, search):
    """Existing callers keep the response shape they had before facet_field existed."""
    mock_search.return_value = SearchResults(**search)
    client.get("/search?q=heart")
    assert mock_search.call_args.kwargs["facet_fields"] == ["category", "in_taxon_label"]


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.search")
def test_search_facet_fields_are_opt_in(mock_search, search):
    mock_search.return_value = SearchResults(**search)
    params = {"q": "heart", "facet_field": ["subsets", "namespace"]}
    client.get(f"/search?{urllib.parse.urlencode(params, doseq=True)}")
    assert mock_search.call_args.kwargs["facet_fields"] == ["subsets", "namespace"]


def test_search_rejects_unknown_facet_field():
    """Faceting an arbitrary field is a cheap way to ask Solr an expensive question."""
    with pytest.raises(RequestValidationError) as excinfo:
        client.get("/search?q=heart&facet_field=description")
    assert excinfo.value.errors()[0]["loc"] == ("query", "facet_field", 0)


def test_search_rejects_unknown_scope():
    with pytest.raises(RequestValidationError) as excinfo:
        client.get("/search?q=heart&scope=martian_disease")
    assert excinfo.value.errors()[0]["loc"] == ("query", "scope")


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
