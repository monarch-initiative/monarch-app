from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from httpx import Response
from monarch_py.api.association import router

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
    client.get(
        "/association?category=biolink%3AAssociation&subject=HGNC%3A0000001&predicate=biolink%3Ainteracts_with&object=MONDO%3A0000001&entity=MONDO%3A0000002&subject_category=biolink%3ADisease&subject_namespace=HGNC&subject_taxon=NCBITaxon%3A1234&object_taxon=NCBITaxon%3A9876&object_category=biolink%3AGene&object_namespace=MONDO&direct=true&format=json&limit=20&offset=0"
    )
    mock_get_assoc.assert_called_with(
        category=["biolink:Association"],
        subject=["HGNC:0000001"],
        predicate=["biolink:interacts_with"],
        object=["MONDO:0000001"],
        entity=["MONDO:0000002"],
        subject_category=["biolink:Disease"],
        subject_namespace=["HGNC"],
        subject_taxon=["NCBITaxon:1234"],
        object_taxon=["NCBITaxon:9876"],
        object_category=["biolink:Gene"],
        object_namespace=["MONDO"],
        direct=True,
        format="json",
        offset=0,
        limit=20,
    )
