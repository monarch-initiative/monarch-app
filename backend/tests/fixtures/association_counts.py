
import pytest

@pytest.fixture
def association_counts():
    return {'items': [{'label': 'Disease Model', 'count': 246, 'category': 'biolink:GenotypeToDiseaseAssociation', 'count_direct': 14, 'count_with_orthologs': None}, {'label': 'Disease to Phenotype', 'count': 4247, 'category': 'biolink:DiseaseToPhenotypicFeatureAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Causal Gene', 'count': 133, 'category': 'biolink:CausalGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Correlated Gene', 'count': 156, 'category': 'biolink:CorrelatedGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Variant to Disease', 'count': 701, 'category': 'biolink:VariantToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Medical Action', 'count': 6, 'category': 'biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Cases', 'count': 136, 'category': 'biolink:CaseToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}]}
