
import pytest

@pytest.fixture
def association_counts():
    return {'items': [{'label': 'Disease to Phenotype', 'count': 4193, 'category': 'biolink:DiseaseToPhenotypicFeatureAssociation'}, {'label': 'Gene to Phenotype', 'count': 2907, 'category': 'biolink:GeneToPhenotypicFeatureAssociation'}, {'label': 'Causal Gene', 'count': 126, 'category': 'biolink:CausalGeneToDiseaseAssociation'}, {'label': 'Correlated Gene', 'count': 150, 'category': 'biolink:CorrelatedGeneToDiseaseAssociation'}, {'label': 'Variant to Disease', 'count': 340, 'category': 'biolink:VariantToDiseaseAssociation'}, {'label': 'Disease Model', 'count': 243, 'category': 'biolink:GenotypeToDiseaseAssociation'}, {'label': 'Medical Action', 'count': 4, 'category': 'biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation'}]}
