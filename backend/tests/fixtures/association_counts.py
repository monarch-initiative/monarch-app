import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {"label": "Phenotypes", "count": 3874, "category": "biolink:DiseaseToPhenotypicFeatureAssociation"},
            {"label": "Causal Genes", "count": 122, "category": "biolink:CausalGeneToDiseaseAssociation"},
            {"label": "Correlated Genes", "count": 140, "category": "biolink:CorrelatedGeneToDiseaseAssociation"},
        ]
    }
