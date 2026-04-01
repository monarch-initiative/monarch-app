
import pytest

@pytest.fixture
def histopheno_query():
    return {'q': '*:*', 'rows': 0, 'start': 0, 'facet': True, 'facet_min_count': 1, 'facet_fields': [], 'facet_queries': ['object_closure:"UPHENO:0002964"', 'object_closure:"UPHENO:0004523"', 'object_closure:"UPHENO:0002764"', 'object_closure:"UPHENO:0002635"', 'object_closure:"UPHENO:0003020"', 'object_closure:"UPHENO:0080362"', 'object_closure:"HP:0001939"', 'object_closure:"UPHENO:0002642"', 'object_closure:"UPHENO:0002833"', 'object_closure:"HP:0002664"', 'object_closure:"UPHENO:0004459"', 'object_closure:"UPHENO:0002948"', 'object_closure:"UPHENO:0003116"', 'object_closure:"UPHENO:0002816"', 'object_closure:"UPHENO:0004536"', 'object_closure:"HP:0000598"', 'object_closure:"UPHENO:0002712"', 'object_closure:"UPHENO:0075949"', 'object_closure:"UPHENO:0049874"', 'object_closure:"UPHENO:0003013"'], 'filter_queries': ['subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121"'], 'facet_mincount': 1, 'query_fields': None, 'def_type': 'edismax', 'q_op': 'AND', 'mm': '100%', 'boost': None, 'sort': None, 'hl': False}
