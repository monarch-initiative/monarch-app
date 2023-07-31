import pytest


@pytest.fixture
def histopheno():
    return {
        "id": "MONDO:0020121",
        "items": [
            {"label": "musculature", "count": 1787, "id": "HP:0003011"},
            {"label": "nervous_system", "count": 1144, "id": "HP:0000707"},
            {"label": "head_neck", "count": 658, "id": "HP:0000152"},
            {"label": "skeletal_system", "count": 627, "id": "HP:0000924"},
            {"label": "respiratory", "count": 333, "id": "HP:0002086"},
            {"label": "eye", "count": 298, "id": "HP:0000478"},
            {"label": "metabolism_homeostasis", "count": 228, "id": "HP:0001939"},
            {"label": "cardiovascular_system", "count": 196, "id": "HP:0001626"},
            {"label": "connective_tissue", "count": 192, "id": "HP:0003549"},
            {"label": "blood", "count": 189, "id": "HP:0001871"},
            {"label": "digestive_system", "count": 176, "id": "HP:0025031"},
            {"label": "integument", "count": 65, "id": "HP:0001574"},
            {"label": "genitourinary_system", "count": 49, "id": "HP:0000119"},
            {"label": "growth", "count": 40, "id": "HP:0001507"},
            {"label": "ear", "count": 32, "id": "HP:0000598"},
            {"label": "endocrine", "count": 27, "id": "HP:0000818"},
            {"label": "immune_system", "count": 24, "id": "HP:0002715"},
            {"label": "prenatal_or_birth", "count": 24, "id": "HP:0001197"},
            {"label": "neoplasm", "count": 8, "id": "HP:0002664"},
            {"label": "breast", "count": 1, "id": "HP:0000769"},
        ],
    }
