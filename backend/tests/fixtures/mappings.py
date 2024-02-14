import pytest


@pytest.fixture
def mappings():
    return {
        "limit": 20,
        "offset": 0,
        "total": 7,
        "items": [
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "DOID:9884",
                "object_label": "muscular dystrophy",
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "5292faf1-de01-4ad1-bff6-f153901a7152",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "ICD10CM:G71.0",
                "object_label": "Muscular dystrophy",
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "aca5243c-67ba-4b1c-ac88-6c53853a2cdb",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "NCIT:C84910",
                "object_label": "Muscular Dystrophy",
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "aa8b03b3-d02f-44b3-9256-8aee2c4400d8",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "Orphanet:98473",
                "object_label": "Muscular dystrophy",
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "f9362b76-05fe-4666-96b0-854bb2898567",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "SCTID:73297009",
                "object_label": None,
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "b889cc72-99b6-423e-932a-4a3b4be9daef",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "UMLS:C0026850",
                "object_label": None,
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "24b22775-d7c7-4aee-ad6d-f61e1fee1ce4",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "mesh:D009136",
                "object_label": None,
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "96aa0222-74bd-4749-b777-ae2632461adf",
            },
        ],
    }
