import pytest


@pytest.fixture
def mapping_response():
    return {
        "responseHeader": {
            "QTime": 0,
            "params": {
                "mm": "100%",
                "q": "*:*",
                "defType": "edismax",
                "facet_min_count": "1",
                "start": "0",
                "q.op": "AND",
                "fq": 'subject_id:"MONDO\\:0020121" OR object_id:"MONDO\\:0020121"',
                "rows": "20",
                "facet": "true",
            },
        },
        "response": {
            "num_found": 7,
            "start": 0,
            "docs": [
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "DOID:9884",
                    "object_label": "muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "63d84b9a-93bc-4d4a-9c2c-755a444f7d7c",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "ICD10CM:G71.0",
                    "object_label": "Muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "1e7e3e71-c912-443f-b92f-c7a828543070",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "NCIT:C84910",
                    "object_label": "Muscular Dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "8b7a5c87-d896-4daf-ac51-6ad53ef838a7",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "Orphanet:98473",
                    "object_label": "Muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "74d9dc89-0a38-41fd-8f0f-9b89e1085824",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "SCTID:73297009",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "f93de036-44d8-43fd-b5b6-9753b75f79b0",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "UMLS:C0026850",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "d5cbdd21-5791-4b49-ae6f-42b8f226e3bf",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "mesh:D009136",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "573ffaec-5e44-47a3-affc-1019df4b4ef9",
                },
            ],
        },
        "facet_counts": {"facet_fields": {}, "facet_queries": {}},
    }
