import urllib

import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response

from monarch_py.api.search import SEARCH_FACET_METHOD, router
from monarch_py.api.utils.entity_fields import entity_fields
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
        "facet_fields": ["category", "in_taxon_label"],
        "highlighting": True,
        # The endpoint restricts both of these; the CLI path deliberately does not, so
        # they have to be passed here rather than defaulted in the query builder.
        "facet_method": SEARCH_FACET_METHOD,
        "fields": entity_fields(include_phenotypes=False, include_descendants=False),
    }
    search_params["category"] = [EntityCategory(c) for c in search_params["category"]]
    search_params["category"] = [EntityCategory.DISEASE, EntityCategory.PHENOTYPIC_FEATURE]
    mock_search.assert_called_with(**search_params)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.autocomplete")
def test_autocomplete_params(mock_autocomplete, autocomplete):
    mock_autocomplete.return_value = autocomplete
    client.get(f"/autocomplete?q=heart")
    mock_autocomplete.assert_called_with(q="heart")


@pytest.mark.parametrize(
    "include_phenotypes,include_descendants",
    [(False, False), (True, False), (False, True), (True, True)],
    ids=["neither", "phenotypes", "descendants", "both"],
)
@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.search")
def test_search_passes_each_include_flag_through(mock_search, search, include_phenotypes, include_descendants):
    """Both flags reach `fields` on the right axis.

    Asserting only the default would let a refactor that swapped these two arguments
    pass, since either ordering produces the same field list when both are off.
    """
    mock_search.return_value = SearchResults(**search)
    client.get(
        f"/search?q=heart&include_phenotypes={str(include_phenotypes).lower()}"
        f"&include_descendants={str(include_descendants).lower()}"
    )
    assert mock_search.call_args.kwargs["fields"] == entity_fields(include_phenotypes, include_descendants)


@pytest.mark.parametrize(
    "include_phenotypes,include_descendants",
    [(False, False), (True, False), (False, True), (True, True)],
    ids=["neither", "phenotypes", "descendants", "both"],
)
@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.ground_entity")
def test_ground_passes_each_include_flag_through(mock_ground, include_phenotypes, include_descendants):
    """Grounding shares the field definition, so it has to share the wiring too."""
    from monarch_py.api.text_annotation import router as annotation_router

    mock_ground.return_value = []
    ground_client = TestClient(annotation_router)
    ground_client.get(
        f"/ground?text=heart&include_phenotypes={str(include_phenotypes).lower()}"
        f"&include_descendants={str(include_descendants).lower()}"
    )
    assert mock_ground.call_args.kwargs["fields"] == entity_fields(include_phenotypes, include_descendants)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.ground_entity")
def test_ground_post_passes_include_flags_through(mock_ground):
    from monarch_py.api.text_annotation import router as annotation_router

    mock_ground.return_value = []
    ground_client = TestClient(annotation_router)
    ground_client.post("/ground", json={"content": "heart", "include_phenotypes": True})
    assert mock_ground.call_args.kwargs["fields"] == entity_fields(include_phenotypes=True, include_descendants=False)
