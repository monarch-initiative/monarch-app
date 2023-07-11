import os
from pathlib import Path

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_query, 
    build_association_counts_query,
    build_autocomplete_query,
    build_histopheno_query, 
    build_search_query
)
from monarch_py.service.solr_service import SolrService, core
from monarch_py.utils.utils import format_output


### Writers

def write_frontend_fixture(key, value):
    format_output("json", value, f"{frontend_fixtures}/{key}.json")


def write_backend_fixture(key, value):
    try:
        contents = value.dict()
    except AttributeError:
        contents = value
    filename = f"{backend_fixtures}/{key.replace('-', '_')}.py"
    file_contents = f"""
import pytest

@pytest.fixture
def {key.replace('-','_')}():
    return {contents}
"""
    with open(f"{filename}", "w") as f:
        f.write(file_contents)


### Check if Solr is available

if not SolrImplementation().solr_is_available():
    raise Exception("Solr is not available. Please try running `monarch solr start` and try again.")

### Define variables

si = SolrImplementation()
solr_url = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")
solr_entities = SolrService(base_url=solr_url, core=core.ENTITY)
solr_associations = SolrService(base_url=solr_url, core=core.ASSOCIATION)

root = Path(__file__).parent.parent
frontend_fixtures = Path(f"{root}/frontend/fixtures")
backend_fixtures = Path(f"{root}/backend/tests/fixtures")

node_id = "MONDO:0020121"


### Generate fixtures

fixtures = {}
fixtures['associations'] = si.get_associations(entity = node_id)
fixtures['association-counts'] = si.get_association_counts(entity = node_id)
# fixtures['association-evidence'] = 
fixtures['autocomplete'] = si.autocomplete("fanc")
# fixtures['datasets'] = 
# fixtures['feedback'] = 
fixtures['histopheno'] = si.get_histopheno(node_id)
fixtures['node'] = si.get_entity(id = node_id, extra = True)
# fixtures['node-publication-abstract'] = 
# fixtures['node-publication-summary'] = 
# fixtures['ontologies'] = 
# fixtures['phenotype-explorer-compare'] = 
# fixtures['phenotype-explorer-search'] = 
fixtures['search'] = si.search(q = "fanconi")
# fixtures['text-annotator'] = 
# fixtures['uptime'] = 

### Generate query fixtures

query_fixtures = {}
query_fixtures['association-counts-query'] = build_association_counts_query(entity=node_id)
query_fixtures['association-query-params'] = {
    "category":["biolink:TestCase"],
    "predicate":["biolink:is_a_test_case", "biolink:is_an_example"],
    "subject":["TEST:0000001"],
    "object":["TEST:0000002"],
    "subject_closure":"TEST:0000003",
    "object_closure":"TEST:0000004",
    "entity":["TEST:0000005"],
    "q":"test:q",
    "offset":100,
    "limit":100,
}
query_fixtures['association-query-direct'] = build_association_query(
    **query_fixtures['association-query-params'],
    direct = True
)
query_fixtures['association-query-indirect'] = build_association_query(
    **query_fixtures['association-query-params'],
    direct = False
)
query_fixtures['autocomplete-query'] = build_autocomplete_query(q = "fanc")
query_fixtures['histopheno-query'] = build_histopheno_query(subject_closure = node_id)
query_fixtures['search-query'] = build_search_query(q = "fanconi")

### Generate solr doc fixtures

query_result_fixtures = {}
query_result_fixtures['association-counts-results'] = solr_associations.query(query_fixtures['association-counts-query'])
query_result_fixtures['association-results'] = solr_associations.query(build_association_query(entity=[node_id]))
query_result_fixtures['autocomplete-results'] = solr_entities.query(query_fixtures['autocomplete-query'])
query_result_fixtures['histopheno-results'] = solr_associations.query(query_fixtures['histopheno-query'])
query_result_fixtures['search-results'] = solr_entities.query(query_fixtures['search-query'])

### Write frontend fixtures
for key, value in fixtures.items():
    format_output("json", value, f"{frontend_fixtures}/{key}.json")


### Write backend fixtures

all_fixtures = {
    **fixtures,
    **query_fixtures,
    **query_result_fixtures
}
for key, value in all_fixtures.items():
    write_backend_fixture(key, value)

