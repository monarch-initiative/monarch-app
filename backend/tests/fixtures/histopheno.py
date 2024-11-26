import pytest


@pytest.fixture
def histopheno():
    return {
        "id": "MONDO:0020121",
        "items": [
            {"label": "musculature", "count": 2057, "id": "UPHENO:0002816"},
            {"label": "nervous_system", "count": 1113, "id": "UPHENO:0004523"},
            {"label": "head_neck", "count": 595, "id": "UPHENO:0002764"},
            {"label": "skeletal_system", "count": 508, "id": "UPHENO:0002964"},
            {"label": "eye", "count": 297, "id": "UPHENO:0003020"},
            {"label": "metabolism_homeostasis", "count": 225, "id": "HP:0001939"},
            {"label": "blood", "count": 183, "id": "UPHENO:0004459"},
            {"label": "connective_tissue", "count": 175, "id": "UPHENO:0002712"},
            {"label": "respiratory", "count": 157, "id": "UPHENO:0004536"},
            {"label": "digestive_system", "count": 153, "id": "UPHENO:0002833"},
            {"label": "integument", "count": 49, "id": "UPHENO:0002635"},
            {"label": "genitourinary_system", "count": 49, "id": "UPHENO:0002642"},
            {"label": "growth", "count": 32, "id": "UPHENO:0049874"},
            {"label": "immune_system", "count": 28, "id": "UPHENO:0002948"},
            {"label": "ear", "count": 26, "id": "HP:0000598"},
            {"label": "endocrine", "count": 25, "id": "UPHENO:0003116"},
            {"label": "prenatal_or_birth", "count": 22, "id": "UPHENO:0075949"},
            {"label": "neoplasm", "count": 7, "id": "HP:0002664"},
            {"label": "breast", "count": 1, "id": "UPHENO:0003013"},
            {"label": "cardiovascular_system", "count": 0, "id": "UPHENO:0080362"},
        ],
    }
