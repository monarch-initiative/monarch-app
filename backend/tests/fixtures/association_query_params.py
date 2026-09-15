
import pytest

@pytest.fixture
def association_query_params():
    return {'category': ['biolink:DiseaseToPhenotypicFeatureAssociation'], 'subject': ['TEST:0000001'], 'subject_closure': 'TEST:0000003', 'subject_category': ['biolink:Gene'], 'subject_namespace': 'TEST', 'subject_taxon': ['NCBITaxon:1111'], 'predicate': ['biolink:causes'], 'object': ['TEST:0000002'], 'object_closure': 'TEST:0000004', 'object_category': ['biolink:Disease'], 'object_namespace': 'TEST', 'object_taxon': ['NCBITaxon:2222'], 'entity': ['TEST:0000005'], 'q': 'test:q', 'offset': 100, 'limit': 100}
