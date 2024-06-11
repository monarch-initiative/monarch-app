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
                    "id": "35dd4712-cbd1-48ca-9ea8-76fc64fd64c6",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "ICD10CM:G71.0",
                    "object_label": "Muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "6993b2bc-dcb1-46a9-a1e7-a7f13538f348",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "NCIT:C84910",
                    "object_label": "Muscular Dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "c316e0c5-432c-4d78-aaee-9e021759557f",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "Orphanet:98473",
                    "object_label": "Muscular dystrophy",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "83793e01-bce0-4bdf-a124-addbef4ba50a",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "SCTID:73297009",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "b56db466-9225-4e9c-97ab-8937bc6e29be",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "UMLS:C0026850",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "f41a4f1a-9898-4452-bbd9-39e028189279",
                },
                {
                    "subject_id": "MONDO:0020121",
                    "subject_label": "muscular dystrophy",
                    "predicate_id": "skos:exactMatch",
                    "object_id": "MESH:D009136",
                    "mapping_justification": "semapv:UnspecifiedMatching",
                    "id": "3dea3a7b-16c5-467a-8976-808f74fce04d",
                },
            ],
        },
        "facet_counts": {"facet_fields": {}, "facet_queries": {}},
    }
