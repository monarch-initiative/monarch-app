import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import MagicMock, patch

from monarch_py.api.additional_models import (
    SemsimMetric,
    SemsimSearchGroup,
    SemsimMultiCompareRequest,
    SemsimDirectionality,
    SemsimSearchMode,
)
from monarch_py.api.semsim import router
from monarch_py.datamodels.category_enums import AssociationPredicate, EntityCategory
from monarch_py.datamodels.model import Entity, SemsimSearchResult

client = TestClient(router)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.autocomplete")
def test_autocomplete_params(mock_autocomplete, autocomplete):
    mock_autocomplete.return_value = autocomplete
    client.get(f"/autocomplete?q=heart")
    mock_autocomplete.assert_called_with(
        q="heart",
        category=[EntityCategory.DISEASE, EntityCategory.GENE, EntityCategory.PHENOTYPIC_FEATURE],
        prioritized_predicates=[AssociationPredicate.HAS_PHENOTYPE],
    )


@pytest.mark.parametrize(
    "metric",
    [
        SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        SemsimMetric.JACCARD_SIMILARITY,
        SemsimMetric.PHENODIGM_SCORE,
    ],
)
@patch("monarch_py.service.semsim_service.SemsimianService.compare")
def test_get_compare(mock_compare, metric):
    mock_compare.return_value = MagicMock()

    subjects = "HP:123,HP:456"
    objects = "HP:789,HP:987"

    response = client.get(f"/compare/{subjects}/{objects}?metric={metric}")

    assert response.status_code == status.HTTP_200_OK
    mock_compare.assert_called_once_with(subjects=["HP:123", "HP:456"], objects=["HP:789", "HP:987"], metric=metric)


@pytest.mark.parametrize(
    "metric",
    [
        SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        SemsimMetric.JACCARD_SIMILARITY,
        SemsimMetric.PHENODIGM_SCORE,
    ],
)
@patch("monarch_py.service.semsim_service.SemsimianService.compare")
def test_post_compare(mock_compare, metric):
    mock_compare.return_value = MagicMock()

    subjects = ["HP:123", "HP:456"]
    objects = ["HP:789", "HP:987"]

    response = client.post(f"/compare/", json={"subjects": subjects, "objects": objects, "metric": metric.value})

    assert response.status_code == status.HTTP_200_OK
    mock_compare.assert_called_once_with(subjects=subjects, objects=objects, metric=metric)


@patch("monarch_py.service.semsim_service.SemsimianService.search")
@pytest.mark.parametrize(
    "termset, metric",
    [
        ("HP:123,HP:456", SemsimMetric.ANCESTOR_INFORMATION_CONTENT),
        ("HP:123, HP:456", SemsimMetric.JACCARD_SIMILARITY),
        (" HP:123, HP:456 ", SemsimMetric.PHENODIGM_SCORE),
    ],
)
def test_get_search(mock_search, termset: str, metric: SemsimMetric):
    mock_search.return_value = MagicMock()

    group = SemsimSearchGroup.HGNC
    limit = 5

    response = client.get(f"/search/{termset}/{group.value}?metric={metric}&limit={limit}")
    directionality = SemsimDirectionality.BIDIRECTIONAL
    assert response.status_code == status.HTTP_200_OK
    mock_search.assert_called_once_with(
        termset=["HP:123", "HP:456"], prefix=group.name, metric=metric, directionality=directionality, limit=limit
    )


@patch("monarch_py.service.semsim_service.SemsimianService.search")
def test_post_search(mock_search):
    mock_search.return_value = MagicMock()

    termset = ["HP:123", "HP:456"]
    group = SemsimSearchGroup.HGNC
    metric = SemsimMetric.JACCARD_SIMILARITY
    directionality = SemsimDirectionality.BIDIRECTIONAL
    limit = 5

    response = client.post(
        f"/search/",
        json={
            "termset": termset,
            "group": group.value,
            "metric": metric,
            "directionality": directionality,
            "limit": limit,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    mock_search.assert_called_once_with(
        termset=["HP:123", "HP:456"],
        prefix=group.name,
        metric=metric,
        directionality=directionality,
        limit=limit,
    )


@patch("monarch_py.service.semsim_service.SemsimianService.multi_compare")
def test_get_multi_compare(mock_multi_compare):
    mock_multi_compare.return_value = MagicMock()

    subjects = ["HP:123", "HP:456"]
    object_sets = [
        {"id": "something1", "label": "Test Set", "phenotypes": ["HP:789", "HP:101112"]},
        {"id": "something2", "label": "Test Set 2", "phenotypes": ["HP:987", "HP:102223"]},
    ]

    response = client.post(
        f"/multicompare/",
        json={
            "subjects": subjects,
            "object_sets": object_sets,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    mock_multi_compare.assert_called_once_with(SemsimMultiCompareRequest(subjects=subjects, object_sets=object_sets))


@patch("monarch_py.api.semsim.semsim_service")
def test_ducksim_only_setting_routes_to_ducksim(mock_semsim_service):
    """semsimian can't run a full search, so a request for one is served by ducksim even when the
    default backend is semsimian, and the response says so."""
    mock_semsim_service.return_value.search.return_value = []
    response = client.get("/search/HP:123/Human Genes?search_mode=full&engine=semsimian")
    assert response.status_code == status.HTTP_200_OK
    mock_semsim_service.assert_called_once_with("ducksim")
    mock_semsim_service.return_value.search.assert_called_once_with(
        termset=["HP:123"],
        prefix="HGNC",
        metric=SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        directionality=SemsimDirectionality.BIDIRECTIONAL,
        limit=10,
        search_mode=SemsimSearchMode.FULL,
    )


@patch("monarch_py.api.semsim.semsim_service")
def test_default_settings_keep_the_configured_backend(mock_semsim_service):
    mock_semsim_service.return_value.search.return_value = []
    client.get("/search/HP:123/Human Genes?engine=semsimian&search_mode=hybrid")
    mock_semsim_service.assert_called_once_with("semsimian")
    assert "search_mode" not in mock_semsim_service.return_value.search.call_args.kwargs


@patch("monarch_py.api.semsim.semsim_service")
def test_compare_directionality_routes_to_ducksim(mock_semsim_service):
    client.get("/compare/HP:1/HP:2?directionality=object_to_subject&engine=semsimian")
    mock_semsim_service.assert_called_once_with("ducksim")
    mock_semsim_service.return_value.compare.assert_called_once_with(
        subjects=["HP:1"],
        objects=["HP:2"],
        metric=SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        directionality=SemsimDirectionality.OBJECT_TO_SUBJECT,
    )


@patch("monarch_py.api.semsim.semsim_service")
def test_bidirectional_compare_keeps_the_configured_backend(mock_semsim_service):
    client.get("/compare/HP:1/HP:2?directionality=bidirectional&engine=semsimian")
    mock_semsim_service.assert_called_once_with("semsimian")
    assert "directionality" not in mock_semsim_service.return_value.compare.call_args.kwargs


@patch("monarch_py.api.semsim.semsim_service")
def test_post_compare_directionality_routes_to_ducksim(mock_semsim_service):
    client.post(
        "/compare/",
        json={"subjects": ["HP:1"], "objects": ["HP:2"], "directionality": "subject_to_object"},
        params={"engine": "semsimian"},
    )
    mock_semsim_service.assert_called_once_with("ducksim")
    assert mock_semsim_service.return_value.compare.call_args.kwargs["directionality"] == (
        SemsimDirectionality.SUBJECT_TO_OBJECT
    )


@patch("monarch_py.api.semsim.semsim_service")
def test_bidirectional_post_compare_keeps_the_configured_backend(mock_semsim_service):
    client.post("/compare/", json={"subjects": ["HP:1"], "objects": ["HP:2"]}, params={"engine": "semsimian"})
    mock_semsim_service.assert_called_once_with("semsimian")
    assert "directionality" not in mock_semsim_service.return_value.compare.call_args.kwargs


MULTICOMPARE_BODY = {"subjects": ["HP:1"], "object_sets": [{"id": "X", "label": "x", "phenotypes": ["HP:2"]}]}


@patch("monarch_py.api.semsim.semsim_service")
def test_multicompare_directionality_routes_to_ducksim(mock_semsim_service):
    """multi_compare reads directionality from the request, so it must not also get it as a kwarg
    (SemsimianService.multi_compare takes none). The response says which engine served it."""
    mock_semsim_service.return_value.multi_compare.return_value = [
        SemsimSearchResult(subject=Entity(id="X", name="x"), score=1.0)
    ]
    response = client.post(
        "/multicompare/",
        json={**MULTICOMPARE_BODY, "directionality": "object_to_subject"},
        params={"engine": "semsimian"},
    )
    assert response.status_code == status.HTTP_200_OK
    mock_semsim_service.assert_called_once_with("ducksim")
    call = mock_semsim_service.return_value.multi_compare.call_args
    assert call.kwargs == {}
    assert call.args[0].directionality == SemsimDirectionality.OBJECT_TO_SUBJECT
    assert response.json()[0]["search_settings"]["engine"] == "ducksim"
    assert response.json()[0]["search_settings"]["directionality"] == "object_to_subject"


@patch("monarch_py.api.semsim.resolve_engine", return_value="semsimian")
@patch("monarch_py.api.semsim.semsim_service")
def test_bidirectional_multicompare_keeps_the_configured_backend(mock_semsim_service, _):
    mock_semsim_service.return_value.multi_compare.return_value = [
        SemsimSearchResult(subject=Entity(id="X", name="x"), score=1.0)
    ]
    response = client.post("/multicompare/", json=MULTICOMPARE_BODY, params={"engine": "semsimian"})
    mock_semsim_service.assert_called_once_with("semsimian")
    assert mock_semsim_service.return_value.multi_compare.call_args.kwargs == {}
    assert response.json()[0]["search_settings"]["engine"] == "semsimian"
