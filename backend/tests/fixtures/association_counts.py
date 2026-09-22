import pytest


@pytest.fixture
def association_counts():
    return {
        "items": [
            {
                "label": "Variant to Disease",
                "count": 6862,
                "key": "biolink:VariantToDiseaseAssociation",
                "category": "biolink:VariantToDiseaseAssociation",
                "count_direct": 22,
                "count_with_orthologs": None,
            },
            {
                "label": "Disease Model",
                "count": 246,
                "key": "biolink:GenotypeAsAModelOfDiseaseAssociation",
                "category": "biolink:GenotypeAsAModelOfDiseaseAssociation",
                "count_direct": 14,
                "count_with_orthologs": None,
            },
            {
                "label": "Disease to Phenotype",
                "count": 4241,
                "key": "biolink:DiseaseToPhenotypicFeatureAssociation",
                "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
                "count_direct": 0,
                "count_with_orthologs": None,
            },
            {
                "label": "Causal Gene",
                "count": 133,
                "key": "biolink:CausalGeneToDiseaseAssociation",
                "category": "biolink:CausalGeneToDiseaseAssociation",
                "count_direct": 0,
                "count_with_orthologs": None,
            },
            {
                "label": "Correlated Gene",
                "count": 156,
                "key": "correlated_gene_to_disease",
                "category": "biolink:GeneToDiseaseAssociation",
                "count_direct": 0,
                "count_with_orthologs": None,
            },
            {
                "label": "Cases",
                "count": 136,
                "key": "biolink:CaseToDiseaseAssociation",
                "category": "biolink:CaseToDiseaseAssociation",
                "count_direct": 0,
                "count_with_orthologs": None,
            },
        ]
    }
