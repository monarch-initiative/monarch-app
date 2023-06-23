from pathlib import Path

# from monarch_py import solr_cli as mpy
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.utils.utils import format_output


### Check if Solr is available
if not SolrImplementation().solr_is_available():
    raise Exception("Solr is not available. Please try running `monarch solr start` and try again.")

si = SolrImplementation()
root = Path(__file__).parent.parent
frontend_fixtures = Path(f"{root}/frontend/fixtures")
backend_fixtures = Path(f"{root}/backend/tests/fixtures")
node_id = "MONDO:0020121"


### Generate fixtures
fixtures = {}
# fixtures['association-evidence'] = 
fixtures['autocomplete'] = si.autocomplete("fanc")
# fixtures['datasets'] = 
# fixtures['feedback'] = 
fixtures['histopheno'] = si.get_histopheno(node_id)
fixtures['node'] = si.get_entity(id = node_id, extra = True)
fixtures['associations'] = si.get_associations(entity = node_id)
# fixtures['node-publication-abstract'] = 
# fixtures['node-publication-summary'] = 
# fixtures['ontologies'] = 
# fixtures['phenotype-explorer-compare'] = 
# fixtures['phenotype-explorer-search'] = 
fixtures['search'] = si.search(q = "fanconi")
# fixtures['text-annotator'] = 
# fixtures['uptime'] = 


### Write frontend fixtures
for key, value in fixtures.items():
    format_output("json", value, f"{frontend_fixtures}/{key}.json")


### Write backend fixtures
for key, value in fixtures.items():
    filename = f"{backend_fixtures}/{key.replace('-', '_')}.py"
    file_contents = f"""
import pytest

@pytest.fixture
def {key.replace('-','_')}():
    return {value.dict()}
"""
    with open(f"{filename}", "w") as f:
        f.write(file_contents)

