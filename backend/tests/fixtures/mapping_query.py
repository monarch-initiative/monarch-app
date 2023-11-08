import pytest


@pytest.fixture
def mapping_query():
    return {
        "q": "*:*",
        "rows": 20,
        "start": 0,
        "facet": True,
        "facet_fields": [],
        "facet_queries": [],
        "filter_queries": ['subject_id:"MONDO\\:0020121" OR object_id:"MONDO\\:0020121"'],
        "query_fields": None,
        "def_type": "edismax",
        "q_op": "AND",
        "mm": "100%",
        "boost": None,
        "sort": None,
        "facet_min_count": 1,
    }
