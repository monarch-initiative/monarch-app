import pytest


@pytest.fixture
def association_table_response():
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
                "fq": [
                    "category:biolink\\:DiseaseToPhenotypicFeatureAssociation",
                    'subject:"MONDO\\:0020121" OR subject_closure:"MONDO\\:0020121" OR object:"MONDO\\:0020121" OR object_closure:"MONDO\\:0020121"',
                ],
                "sort": "evidence_count desc, subject_label asc, predicate asc, object_label asc, primary_knowledge_source asc",
                "rows": "5",
                "facet": "true",
            },
        },
        "response": {"num_found": 0, "start": 0, "docs": []},
        "facet_counts": {"facet_fields": {}, "facet_queries": {}},
    }
