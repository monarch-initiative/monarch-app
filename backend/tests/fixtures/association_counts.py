import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {
                "label": "Phenotypes",
                "count": 4009,
                "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            },
            {
                "label": "Causal Genes",
                "count": 122,
                "category": "biolink:CausalGeneToDiseaseAssociation",
            },
            {
                "label": "Correlated Genes",
                "count": 150,
                "category": "biolink:CorrelatedGeneToDiseaseAssociation",
            },
        ]
    }
