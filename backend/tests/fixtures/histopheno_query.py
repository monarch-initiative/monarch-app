import pytest


@pytest.fixture
def histopheno_query():
    return {
        "q": "*:*",
        "rows": 0,
        "start": 0,
        "facet": True,
        "facet_fields": [],
        "facet_queries": [
            'object_closure:"HP:0000924"',
            'object_closure:"HP:0000707"',
            'object_closure:"HP:0000152"',
            'object_closure:"HP:0001574"',
            'object_closure:"HP:0000478"',
            'object_closure:"HP:0001626"',
            'object_closure:"HP:0001939"',
            'object_closure:"HP:0000119"',
            'object_closure:"HP:0025031"',
            'object_closure:"HP:0002664"',
            'object_closure:"HP:0001871"',
            'object_closure:"HP:0002715"',
            'object_closure:"HP:0000818"',
            'object_closure:"HP:0003011"',
            'object_closure:"HP:0002086"',
            'object_closure:"HP:0000598"',
            'object_closure:"HP:0003549"',
            'object_closure:"HP:0001197"',
            'object_closure:"HP:0001507"',
            'object_closure:"HP:0000769"',
        ],
        "filter_queries": ["subject_closure:MONDO\\:0020121"],
        "query_fields": None,
        "def_type": "edismax",
        "q_op": "AND",
        "mm": "100%",
        "boost": None,
        "sort": None,
        "facet_min_count": 1,
    }
