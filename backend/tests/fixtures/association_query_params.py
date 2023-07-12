import pytest


@pytest.fixture
def association_query_params():
    return {
        "category": ["biolink:TestCase"],
        "predicate": ["biolink:is_a_test_case", "biolink:is_an_example"],
        "subject": ["TEST:0000001"],
        "object": ["TEST:0000002"],
        "subject_closure": "TEST:0000003",
        "object_closure": "TEST:0000004",
        "entity": ["TEST:0000005"],
        "q": "test:q",
        "offset": 100,
        "limit": 100,
    }
