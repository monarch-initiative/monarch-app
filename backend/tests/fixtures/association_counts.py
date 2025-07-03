import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {
                "label": "Disease to Phenotype",
                "count": 4192,
                "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            },
            {"label": "Gene to Phenotype", "count": 6475, "category": "biolink:GeneToPhenotypicFeatureAssociation"},
            {"label": "Causal Gene", "count": 126, "category": "biolink:CausalGeneToDiseaseAssociation"},
            {"label": "Correlated Gene", "count": 149, "category": "biolink:CorrelatedGeneToDiseaseAssociation"},
            {"label": "Variant to Disease", "count": 211, "category": "biolink:VariantToDiseaseAssociation"},
            {"label": "Disease Model", "count": 242, "category": "biolink:GenotypeToDiseaseAssociation"},
            {
                "label": "Medical Action",
                "count": 4,
                "category": "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation",
            },
        ]
    }
