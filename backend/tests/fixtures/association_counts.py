import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {
                "label": "Phenotypes",
                "count": 4312,
                "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            },
            {
                "label": "Causal Genes",
                "count": 123,
                "category": "biolink:CausalGeneToDiseaseAssociation",
            },
            {
                "label": "Correlated Genes",
                "count": 149,
                "category": "biolink:CorrelatedGeneToDiseaseAssociation",
            },
        ]
    }
