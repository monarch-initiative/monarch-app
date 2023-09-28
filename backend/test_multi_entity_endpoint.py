from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.utils.utils import to_json
from pprint import pprint

si = SolrImplementation()

results = si.get_multi_entity_associations(
    entity=["MONDO:0012933", "MONDO:0005439", "MANGO:0023456"], counterpart_category=["biolink:PhenotypicQuality", "biolink:Disease"]
)
print(len(results))
count = 0
for i in results:
    count += 1
    to_json(i, file=f"test_multi_endpoint_{count}.json")