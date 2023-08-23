import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {"label": "Phenotypes", "count": 4011, "category": "biolink:DiseaseToPhenotypicFeatureAssociation"},
            {"label": "Causal Genes", "count": 121, "category": "biolink:CausalGeneToDiseaseAssociation"},
            {"label": "Correlated Genes", "count": 147, "category": "biolink:CorrelatedGeneToDiseaseAssociation"},
        ]
    }
