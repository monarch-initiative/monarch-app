
import pytest

@pytest.fixture
def association_counts():
    return {'items': [{'label': 'Variant to Disease', 'count': 6862, 'category': 'biolink:VariantToDiseaseAssociation', 'count_direct': 22, 'count_with_orthologs': None}, {'label': 'Disease Model', 'count': 246, 'category': 'biolink:GenotypeToDiseaseAssociation', 'count_direct': 14, 'count_with_orthologs': None}, {'label': 'Disease to Phenotype', 'count': 4241, 'category': 'biolink:DiseaseToPhenotypicFeatureAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Causal Gene', 'count': 133, 'category': 'biolink:CausalGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Correlated Gene', 'count': 156, 'category': 'biolink:CorrelatedGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Cases', 'count': 136, 'category': 'biolink:CaseToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}]}
