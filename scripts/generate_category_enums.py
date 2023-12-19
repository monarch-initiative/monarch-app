"""
Generates category enums for the API using Solr queries against the Monarch KG.
Requires a running Monarch Solr instance.
"""
import os
import requests
from pathlib import Path

from monarch_py.implementations.solr.solr_implementation import SolrImplementation


si = SolrImplementation()
solr_url = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")
root = Path(__file__).parent.parent
output_file = Path(root) / "backend" / "src" / "monarch_py" / "datamodels" / "category_enums.py"

association_facets = "http://localhost:8983/solr/association/select?wt=json&rows=0&q=*:*&facet=true&facet.field=category&facet.field=predicate"
entity_facets = "http://localhost:8983/solr/entity/select?wt=json&rows=0&q=*:*&facet=true&facet.field=category"

association_facets_response = requests.get(association_facets)
entity_facets_response = requests.get(entity_facets)

entity_categories = entity_facets_response.json()["facet_counts"]["facet_fields"]["category"]
association_categories = association_facets_response.json()["facet_counts"]["facet_fields"]["category"]
association_predicates = association_facets_response.json()["facet_counts"]["facet_fields"]["predicate"]

entity_categories = [x.replace("biolink:", "") for x in entity_categories if isinstance(x, str)]
association_categories = [x.replace("biolink:", "") for x in association_categories if isinstance(x, str)]
association_predicates = [x.replace("biolink:", "") for x in association_predicates if isinstance(x, str)]

entity_category_entries = []
for category in entity_categories:
    entity_category_entries.append(f"{category.upper()} = '{category}'\n    ")

association_category_entries = []
for category in association_categories:
    association_category_entries.append(f"{category.upper()} = '{category}'\n    ")

association_predicate_entries = []
for category in association_predicates:
    association_predicate_entries.append(f"{category.upper()} = '{category}'\n    ")

output = f'''from enum import Enum


class EntityCategory(Enum):
    """Entity categories"""
    {''.join(entity_category_entries)}

class AssociationCategory(Enum):
    """Association categories"""
    {''.join(association_category_entries)}    

class AssociationPredicate(Enum):
    """Association predicates"""
    {''.join(association_predicate_entries)}
'''

with open(output_file, "w") as f:
    f.write(output)
