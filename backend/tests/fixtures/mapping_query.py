
import pytest

@pytest.fixture
def mapping_query():
    return {'q': '*:*', 'rows': 20, 'start': 0, 'facet': True, 'facet_min_count': 1, 'facet_fields': [], 'facet_queries': [], 'filter_queries': ['subject_id:"MONDO\\:0020121" OR object_id:"MONDO\\:0020121"'], 'facet_mincount': 1, 'query_fields': None, 'def_type': 'edismax', 'q_op': 'AND', 'mm': '100%', 'boost': None, 'sort': None, 'hl': False}
