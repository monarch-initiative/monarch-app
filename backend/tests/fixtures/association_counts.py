import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {"label": "Phenotypes", "count": 3873, "category": "biolink:DiseaseToPhenotypicFeatureAssociation"},
            {"label": "Causal Genes", "count": 124, "category": "biolink:CausalGeneToDiseaseAssociation"},
            {"label": "Correlated Genes", "count": 139, "category": "biolink:CorrelatedGeneToDiseaseAssociation"},
        ]
    }
