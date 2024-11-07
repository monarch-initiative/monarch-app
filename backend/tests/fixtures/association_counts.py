import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {
                "label": "Disease to Phenotype",
                "count": 4115,
                "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            },
            {"label": "Causal Gene", "count": 126, "category": "biolink:CausalGeneToDiseaseAssociation"},
            {"label": "Correlated Gene", "count": 151, "category": "biolink:CorrelatedGeneToDiseaseAssociation"},
            {"label": "Variant to Disease", "count": 1, "category": "biolink:VariantToDiseaseAssociation"},
            {"label": "Disease Model", "count": 237, "category": "biolink:GenotypeToDiseaseAssociation"},
        ]
    }
