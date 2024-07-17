import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import MagicMock, patch

from monarch_py.api.additional_models import (
    SemsimMetric,
    SemsimSearchGroup,
    SemsimMultiCompareRequest,
    SemsimDirectionality,
)
from monarch_py.api.semsim import router
from monarch_py.datamodels.category_enums import AssociationPredicate, EntityCategory

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
    mock_search.assert_called_once_with(termset=["HP:123", "HP:456"], prefix=group.name, metric=metric, limit=limit)


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
