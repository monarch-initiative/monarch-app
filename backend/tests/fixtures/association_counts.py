
import pytest

@pytest.fixture
def association_counts():
    return {'items': [{'label': 'Disease to Phenotype', 'count': 4161, 'category': 'biolink:DiseaseToPhenotypicFeatureAssociation'}, {'label': 'Causal Gene', 'count': 130, 'category': 'biolink:CausalGeneToDiseaseAssociation'}, {'label': 'Correlated Gene', 'count': 150, 'category': 'biolink:CorrelatedGeneToDiseaseAssociation'}, {'label': 'Variant to Disease', 'count': 435, 'category': 'biolink:VariantToDiseaseAssociation'}, {'label': 'Disease Model', 'count': 244, 'category': 'biolink:GenotypeToDiseaseAssociation'}, {'label': 'Medical Action', 'count': 4, 'category': 'biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation'}, {'label': 'Cases', 'count': 136, 'category': 'biolink:CaseToDiseaseAssociation'}]}
