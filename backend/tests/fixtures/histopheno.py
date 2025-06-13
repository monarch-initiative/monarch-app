import pytest


@pytest.fixture
def histopheno():
    return {
        "id": "MONDO:0020121",
        "items": [
            {"label": "musculature", "count": 2119, "id": "UPHENO:0002816"},
            {"label": "nervous_system", "count": 1059, "id": "UPHENO:0004523"},
            {"label": "head_neck", "count": 606, "id": "UPHENO:0002764"},
            {"label": "skeletal_system", "count": 523, "id": "UPHENO:0002964"},
            {"label": "eye", "count": 299, "id": "UPHENO:0003020"},
            {"label": "metabolism_homeostasis", "count": 230, "id": "HP:0001939"},
            {"label": "blood", "count": 204, "id": "UPHENO:0004459"},
            {"label": "connective_tissue", "count": 187, "id": "UPHENO:0002712"},
            {"label": "digestive_system", "count": 166, "id": "UPHENO:0002833"},
            {"label": "respiratory", "count": 161, "id": "UPHENO:0004536"},
            {"label": "integument", "count": 51, "id": "UPHENO:0002635"},
            {"label": "genitourinary_system", "count": 48, "id": "UPHENO:0002642"},
            {"label": "growth", "count": 32, "id": "UPHENO:0049874"},
            {"label": "immune_system", "count": 28, "id": "UPHENO:0002948"},
            {"label": "endocrine", "count": 28, "id": "UPHENO:0003116"},
            {"label": "ear", "count": 23, "id": "HP:0000598"},
            {"label": "prenatal_or_birth", "count": 22, "id": "UPHENO:0075949"},
            {"label": "neoplasm", "count": 7, "id": "HP:0002664"},
            {"label": "breast", "count": 1, "id": "UPHENO:0003013"},
            {"label": "cardiovascular_system", "count": 0, "id": "UPHENO:0080362"},
        ],
    }
