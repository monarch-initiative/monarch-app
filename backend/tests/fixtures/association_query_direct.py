import pytest


@pytest.fixture
def association_query_direct():
    return {
        "q": "test:q",
        "rows": 100,
        "start": 100,
        "facet": True,
        "facet_min_count": 1,
        "facet_fields": [],
        "facet_queries": [],
        "filter_queries": [
            "category:biolink\\:TestCase",
            "predicate:biolink\\:is_a_test_case OR predicate:biolink\\:is_an_example",
            "subject:TEST\\:0000001",
            "subject_closure:TEST\\:0000003",
            "object:TEST\\:0000002",
            "object_closure:TEST\\:0000004",
            'subject:"TEST\\:0000005" OR object:"TEST\\:0000005"',
        ],
        "query_fields": "subject subject_label^2 subject_label_t subject_closure subject_closure_label subject_closure_label_t predicate predicate_t object object_label^2 object_label_t object_closure object_closure_label object_closure_label_t publications has_evidence primary_knowledge_source aggregator_knowledge_source provided_by ",
        "def_type": "edismax",
        "q_op": "AND",
        "mm": "100%",
        "boost": None,
        "sort": None,
    }
