import pytest


@pytest.fixture
def histopheno():
    return {
        "id": "MONDO:0020121",
        "items": [
            {"label": "musculature", "count": 1709, "id": "UPHENO:0002816"},
            {"label": "nervous_system", "count": 1088, "id": "UPHENO:0004523"},
            {"label": "head_neck", "count": 584, "id": "UPHENO:0002764"},
            {"label": "skeletal_system", "count": 472, "id": "UPHENO:0002964"},
            {"label": "eye", "count": 291, "id": "UPHENO:0003020"},
            {"label": "metabolism_homeostasis", "count": 222, "id": "HP:0001939"},
            {"label": "cardiovascular_system", "count": 181, "id": "UPHENO:0080362"},
            {"label": "blood", "count": 179, "id": "UPHENO:0004459"},
            {"label": "connective_tissue", "count": 162, "id": "UPHENO:0002712"},
            {"label": "respiratory", "count": 155, "id": "UPHENO:0004536"},
            {"label": "neoplasm", "count": 153, "id": "HP:0002664"},
            {"label": "digestive_system", "count": 147, "id": "UPHENO:0002833"},
            {"label": "integument", "count": 47, "id": "UPHENO:0002635"},
            {"label": "genitourinary_system", "count": 44, "id": "UPHENO:0002642"},
            {"label": "growth", "count": 32, "id": "UPHENO:0049874"},
            {"label": "ear", "count": 28, "id": "HP:0000598"},
            {"label": "endocrine", "count": 25, "id": "UPHENO:0003116"},
            {"label": "immune_system", "count": 22, "id": "UPHENO:0002948"},
            {"label": "prenatal_or_birth", "count": 21, "id": "UPHENO:0075949"},
            {"label": "breast", "count": 1, "id": "UPHENO:0003013"},
        ],
    }
