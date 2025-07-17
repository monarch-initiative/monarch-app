from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from monarch_py.api.infores import router
from monarch_py.datamodels.model import InformationResource

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_infores_catalog")
def test_get_infores_catalog_json(mock_get_infores_catalog):
    """Test infores catalog endpoint returns JSON format correctly"""
    mock_data = [
        InformationResource(
            id="infores:agrkb",
            status="released",
            name="Alliance of Genome Resources (AGR Knowledgebase)",
            xref=["https://github.com/NCATSTranslator/Translator-All/wiki/Alliance-of-Genome-Resources"],
            synonym=["ALLIANCE"],
            knowledge_level="knowledge_assertion",
            agent_type="not_provided",
            consumed_by=["infores:biothings-agr"],
        ),
        InformationResource(
            id="infores:aact",
            status="released",
            name="Aggregate Analysis of ClinicalTrial.gov (AACT) database",
            xref=["https://aact.ctti-clinicaltrials.org/"],
            synonym=["AACT"],
            knowledge_level="knowledge_assertion",
            agent_type="not_provided",
        ),
    ]
    mock_get_infores_catalog.return_value = mock_data

    response = client.get("/?format=json")

    assert response.status_code == 200
    assert response.json() == [item.model_dump() for item in mock_data]
    mock_get_infores_catalog.assert_called_once()


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_infores_catalog")
def test_get_infores_catalog_default_format(mock_get_infores_catalog):
    """Test infores catalog endpoint defaults to JSON format"""
    mock_data = [InformationResource(id="infores:test", status="released", knowledge_level="knowledge_assertion", agent_type="not_provided")]
    mock_get_infores_catalog.return_value = mock_data

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == [item.model_dump() for item in mock_data]
    mock_get_infores_catalog.assert_called_once()


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_infores_catalog")
def test_get_infores_catalog_tsv(mock_get_infores_catalog):
    """Test infores catalog endpoint returns TSV format correctly"""
    mock_data = [InformationResource(id="infores:agrkb", status="released", name="Alliance of Genome Resources", knowledge_level="knowledge_assertion", agent_type="not_provided")]
    mock_get_infores_catalog.return_value = mock_data

    response = client.get("/?format=tsv")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/tab-separated-values; charset=utf-8"
    assert "infores:agrkb" in response.text


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_infores")
def test_get_infores_by_id_json(mock_get_infores):
    """Test individual infores endpoint returns JSON format correctly"""
    mock_data = InformationResource(
        id="infores:agrkb",
        status="released",
        name="Alliance of Genome Resources (AGR Knowledgebase)",
        xref=["https://github.com/NCATSTranslator/Translator-All/wiki/Alliance-of-Genome-Resources"],
        synonym=["ALLIANCE"],
        knowledge_level="knowledge_assertion",
        agent_type="not_provided",
        consumed_by=["infores:biothings-agr"],
    )
    mock_get_infores.return_value = mock_data

    response = client.get("/infores:agrkb?format=json")

    assert response.status_code == 200
    assert response.json() == mock_data.model_dump()
    mock_get_infores.assert_called_once_with("infores:agrkb")


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_infores")
def test_get_infores_by_id_not_found(mock_get_infores):
    """Test individual infores endpoint returns 404 for non-existent ID"""
    mock_get_infores.return_value = None

    response = client.get("/infores:nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "Information resource not found"
    mock_get_infores.assert_called_once_with("infores:nonexistent")


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_infores")
def test_get_infores_by_id_tsv(mock_get_infores):
    """Test individual infores endpoint returns TSV format correctly"""
    mock_data = InformationResource(id="infores:agrkb", status="released", name="Alliance of Genome Resources", knowledge_level="knowledge_assertion", agent_type="not_provided")
    mock_get_infores.return_value = mock_data

    response = client.get("/infores:agrkb?format=tsv")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/tab-separated-values; charset=utf-8"
    assert "infores:agrkb" in response.text


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_infores_catalog")
def test_get_infores_catalog_empty_response(mock_get_infores_catalog):
    """Test infores catalog endpoint handles empty response correctly"""
    mock_get_infores_catalog.return_value = []

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == []
    mock_get_infores_catalog.assert_called_once()
