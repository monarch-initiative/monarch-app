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
                "id": "2072e221-f2e9-4d77-8835-239f77ad6475",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "ICD10CM:G71.0",
                "object_label": "Muscular dystrophy",
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "ed9c20b7-84ce-4b8e-80a4-0eb4d23d88bb",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "NCIT:C84910",
                "object_label": "Muscular Dystrophy",
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "91b0c57b-b58d-457e-877f-b98ded88b124",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "Orphanet:98473",
                "object_label": "Muscular dystrophy",
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "6f744251-4221-4a3f-af95-56706940dce8",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "SCTID:73297009",
                "object_label": None,
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "acc8cd04-8e00-43d6-a85c-56cea521ce10",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "UMLS:C0026850",
                "object_label": None,
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "f15f2ef9-8f70-4a02-95fe-ee884bfdfd20",
            },
            {
                "subject_id": "MONDO:0020121",
                "subject_label": "muscular dystrophy",
                "predicate_id": "skos:exactMatch",
                "object_id": "mesh:D009136",
                "object_label": None,
                "mapping_justification": "semapv:UnspecifiedMatching",
                "id": "e418ac4d-ad01-45fa-ae25-e58c06b201c7",
            },
        ],
    }
