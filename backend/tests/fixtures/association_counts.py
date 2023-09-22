import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {
                "label": "Phenotypes",
                "count": 2166,
                "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            },
            {
                "label": "Causal Genes",
                "count": 124,
                "category": "biolink:CausalGeneToDiseaseAssociation",
            },
        ]
    }
