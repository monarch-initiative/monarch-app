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
                    "id": "688da9e1-e4fe-4d27-b079-43c151110ddc",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "ICD10CM:G71.0",
                    "object_label": "Muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "d2172851-2275-422e-ad9a-a7413b21290a",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "NCIT:C84910",
                    "object_label": "Muscular Dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "f605c0b9-7ed5-419f-96e7-226fea68b3ca",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "Orphanet:98473",
                    "object_label": "Muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "c30f86ba-1354-4546-b589-219f1de0a87d",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "SCTID:73297009",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "df261c9b-989a-4df6-a2ec-63bb23199520",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "UMLS:C0026850",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "087e7a60-672d-45b7-bcb0-0132b9be168d",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "mesh:D009136",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "7c30b050-9ccf-49d5-a9c7-9ff16f527538",
                },
            ],
        },
        "facet_counts": {"facet_fields": {}, "facet_queries": {}},
    }
