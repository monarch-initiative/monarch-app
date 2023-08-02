import os
from pathlib import Path

from monarch_py.implementations.oak.oak_implementation import OakImplementation
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_query,
    build_association_counts_query,
    build_autocomplete_query,
    build_histopheno_query,
    build_search_query,
    build_association_table_query
)
from monarch_py.service.solr_service import SolrService, core
from monarch_py.utils.utils import format_output


### Writers

def write_frontend_fixture(key, value):
    try: 
        format_output("json", value, f"{frontend_fixtures}/{key}.json")
    except AttributeError:
        raise Exception("The value passed to write_frontend_fixture must be a pydantic dataclass.")


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

oak = OakImplementation()
si = SolrImplementation()
solr_url = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")
solr_entities = SolrService(base_url=solr_url, core=core.ENTITY)
solr_associations = SolrService(base_url=solr_url, core=core.ASSOCIATION)

root = Path(__file__).parent.parent
frontend_fixtures = Path(f"{root}/frontend/fixtures")
backend_fixtures = Path(f"{root}/backend/tests/fixtures")

NODE_ID = "MONDO:0020121"
CATEGORY = "biolink:DiseaseToPhenotypicFeatureAssociation"


### Generate fixtures

fixtures = {}
fixtures['associations'] = si.get_associations(entity = NODE_ID)
fixtures['association-counts'] = si.get_association_counts(entity = NODE_ID)
fixtures['association-table'] = si.get_association_table(entity=NODE_ID, category=CATEGORY, offset=0, limit=5)
# fixtures['association-evidence'] = 
fixtures['autocomplete'] = si.autocomplete("fanc")
# fixtures['datasets'] = 
# fixtures['feedback'] = 
fixtures['histopheno'] = si.get_histopheno(NODE_ID)
fixtures['entity'] = si.get_entity(id = NODE_ID, extra = False)
fixtures['node'] = si.get_entity(id = NODE_ID, extra = True)
# fixtures['node-publication-abstract'] = 
# fixtures['node-publication-summary'] = 
# fixtures['ontologies'] = 
# fixtures['phenotype-explorer-compare'] = 
# fixtures['phenotype-explorer-search'] = 
fixtures['search'] = si.search(q = "fanconi")
# fixtures['text-annotator'] = 
# fixtures['uptime'] = 

## Leave compare out unless we need it, since it takes a long time to run
# fixtures['compare'] = oak.compare(subjects = ['MP:0010771', 'MP:0002169'], objects = ['HP:0004325'])


### Generate query fixtures

query_fixtures = {}
query_fixtures['association-counts-query'] = build_association_counts_query(entity=NODE_ID)
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
query_fixtures['histopheno-query'] = build_histopheno_query(subject_closure = NODE_ID)
query_fixtures['search-query'] = build_search_query(q = "fanconi")

### Generate query response fixtures

query_response_fixtures = {}
query_response_fixtures['association-response'] = solr_associations.query(build_association_query(entity=[NODE_ID]))
query_response_fixtures['association-counts-response'] = solr_associations.query(query_fixtures['association-counts-query'])
query_response_fixtures['association-table-response'] = solr_associations.query(
    build_association_table_query(entity=NODE_ID, category=CATEGORY)
)
query_response_fixtures['autocomplete-response'] = solr_entities.query(query_fixtures['autocomplete-query'])
query_response_fixtures['entity-response'] = solr_entities.get(NODE_ID)
query_response_fixtures['histopheno-response'] = solr_associations.query(query_fixtures['histopheno-query'])
query_response_fixtures['search-response'] = solr_entities.query(query_fixtures['search-query'])

### Write frontend fixtures
for key, value in fixtures.items():
    write_frontend_fixture(key, value)


### Write backend fixtures
all_fixtures = {
    **fixtures,
    **query_fixtures,
    **query_response_fixtures
}
for key, value in all_fixtures.items():
    write_backend_fixture(key, value)

