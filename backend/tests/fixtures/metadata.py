import pytest


@pytest.fixture
def metadata():
    return [
        {"label": "biolink:Gene", "count": 514018},
        {"label": "biolink:PhenotypicQuality", "count": 89431},
        {"label": "biolink:Disease", "count": 26469},
        {"label": "biolink:GeneToPhenotypicFeatureAssociation", "count": 735039},
        {"label": "biolink:DiseaseToPhenotypicFeatureAssociation", "count": 241110},
        {"label": "biolink:CorrelatedGeneToDiseaseAssociation", "count": 8519},
        {"label": "biolink:CausalGeneToDiseaseAssociation", "count": 6491},
    ]
