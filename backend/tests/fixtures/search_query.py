
import pytest

@pytest.fixture
def search_query():
    return {'q': 'fanconi', 'rows': 20, 'start': 0, 'facet': True, 'facet_min_count': 1, 'facet_fields': [], 'facet_queries': [], 'filter_queries': ['name:*'], 'facet_mincount': 1, 'query_fields': 'id^100 name^10 name_t^5 name_ac symbol^10 symbol_t^5 symbol_ac synonym synonym_t synonym_ac description_t xref', 'def_type': 'edismax', 'q_op': 'AND', 'mm': '100%', 'boost': 'product(if(termfreq(category,"biolink:PhenotypicFeature"),1.1,1),if(termfreq(category,"biolink:Disease"),1.3,1),if(and(termfreq(in_taxon,"NCBITaxon:9606"),termfreq(category,"biolink:Gene")),1.1,1),if(termfreq(deprecated,"true"),0.1,1))', 'sort': None, 'hl': False}
