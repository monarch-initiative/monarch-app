import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {
                "label": "Disease to Phenotype",
                "count": 4077,
                "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            },
            {"label": "Gene to Phenotype", "count": 6350, "category": "biolink:GeneToPhenotypicFeatureAssociation"},
            {"label": "Causal Gene", "count": 125, "category": "biolink:CausalGeneToDiseaseAssociation"},
            {"label": "Correlated Gene", "count": 150, "category": "biolink:CorrelatedGeneToDiseaseAssociation"},
            {"label": "Variant to Disease", "count": 1, "category": "biolink:VariantToDiseaseAssociation"},
            {"label": "Disease Model", "count": 239, "category": "biolink:GenotypeToDiseaseAssociation"},
            {
                "label": "Medical Action",
                "count": 4,
                "category": "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation",
            },
        ]
    }
