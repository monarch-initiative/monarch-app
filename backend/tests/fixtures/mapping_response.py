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
                    "id": "cda26856-16a7-499c-956f-119cbaac5b96",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "ICD10CM:G71.0",
                    "object_label": "Muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "25777569-b997-4c8f-a1f3-5af352a16ee1",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "MESH:D009136",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "819ab197-2ab1-4b73-8d0f-d7d4ec14d8a7",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "NCIT:C84910",
                    "object_label": "Muscular Dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "adb4b8ed-c4dc-4353-a08e-a4cb02b1826e",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "SCTID:73297009",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "f6417283-c9d1-4289-aee6-16d30a4445b1",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "UMLS:C0026850",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "93968631-eedb-448b-b58a-e31e3e411dde",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "Orphanet:98473",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "e39e8ba9-8d7e-4b33-9f46-3867b652bdb5",
                },
            ],
        },
        "facet_counts": {"facet_fields": {}, "facet_queries": {}},
    }
