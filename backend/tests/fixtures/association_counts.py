
import pytest

@pytest.fixture
def association_counts():
    return {'items': [{'label': 'Disease Model', 'count': 240, 'category': 'biolink:GenotypeToDiseaseAssociation', 'count_direct': 13, 'count_with_orthologs': None}, {'label': 'Disease to Phenotype', 'count': 4226, 'category': 'biolink:DiseaseToPhenotypicFeatureAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Causal Gene', 'count': 130, 'category': 'biolink:CausalGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Correlated Gene', 'count': 152, 'category': 'biolink:CorrelatedGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Variant to Disease', 'count': 483, 'category': 'biolink:VariantToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Medical Action', 'count': 10, 'category': 'biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Cases', 'count': 136, 'category': 'biolink:CaseToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}]}
