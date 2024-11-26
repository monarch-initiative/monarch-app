import urllib
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response

from monarch_py.api.association import router
from monarch_py.datamodels.category_enums import AssociationCategory, AssociationPredicate, EntityCategory

client = TestClient(router)


def test_associations(associations):
    with patch.object(
        client,
        "get",
        MagicMock(return_value=Response(200, json=associations, headers={"content-type": "application/json"})),
    ):
        response = client.get("/association?subject=MONDO:0019391&object=HP:0000001")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == associations


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_associations")
def test_associations_params(mock_get_assoc):
    """Test that the correct parameters are passed to the monarch api"""
    mock_get_assoc.return_value = MagicMock()

    params = {
        "category": ["biolink:Association", "biolink:GeneToPhenotypicFeatureAssociation"],
        "subject": ["HGNC:0000001", "HGNC:0000002"],
        "predicate": ["biolink:interacts_with"],
        "object": ["MONDO:0000001", "MONDO:0000002"],
        "entity": ["MONDO:0000002", "HGNC:0000001"],
        "subject_category": ["biolink:Disease", "biolink:Gene"],
        "subject_namespace": ["HGNC", "ZFIN"],
        "subject_taxon": ["NCBITaxon:1234", "NCBITaxon:1"],
        "object_taxon": ["NCBITaxon:9876", "NCBITaxon:2"],
        "object_category": ["biolink:Gene", "biolink:PhenotypicFeature"],
        "object_namespace": ["MONDO", "HP"],
        "direct": True,
        "compact": True,
        "facet_fields": [],
        "facet_queries": [],
        "filter_queries": [],
        "offset": 0,
        "limit": 20,
    }
    query_string = urllib.parse.urlencode(params, doseq=True)
    print(query_string)
    client.get(f"/all?{query_string}")

    params["category"] = [AssociationCategory.ASSOCIATION, AssociationCategory.GENE_TO_PHENOTYPIC_FEATURE_ASSOCIATION]
    params["subject_category"] = [EntityCategory.DISEASE, EntityCategory.GENE]
    params["object_category"] = [EntityCategory.GENE, EntityCategory.PHENOTYPIC_FEATURE]
    params["predicate"] = [AssociationPredicate.INTERACTS_WITH]
    mock_get_assoc.assert_called_with(**params)
