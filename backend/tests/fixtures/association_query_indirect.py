import pytest


@pytest.fixture
def association_query_indirect():
    return {
        "q": "*test:q*",
        "rows": 100,
        "start": 100,
        "facet": True,
        "facet_min_count": 1,
        "facet_fields": [],
        "facet_queries": [],
        "filter_queries": [
            "category:biolink\\:TestCase",
            "predicate:biolink\\:is_a_test_case OR predicate:biolink\\:is_an_example",
            'subject:"TEST:0000001" OR subject_closure:"TEST:0000001"',
            "subject_closure:TEST\\:0000003",
            'object:"TEST:0000002" OR object_closure:"TEST:0000002"',
            "object_closure:TEST\\:0000004",
            'subject:"TEST\\:0000005" OR subject_closure:"TEST\\:0000005" OR object:"TEST\\:0000005" OR object_closure:"TEST\\:0000005"',
        ],
        "query_fields": "subject subject_label predicate object object_label",
        "def_type": "edismax",
        "q_op": "AND",
        "mm": "100%",
        "boost": None,
        "sort": None,
    }
