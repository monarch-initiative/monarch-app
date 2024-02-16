"""
Generates category enums for the API using Solr queries against the Monarch KG.
Requires a running Monarch Solr instance.
"""
import os
import re
import requests
from pathlib import Path

from monarch_py.implementations.solr.solr_implementation import SolrImplementation


si = SolrImplementation()
solr_url = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")

root = Path(__file__).parent.parent
output_file = (
    Path(root) / "backend" / "src" / "monarch_py" / "datamodels" / "category_enums.py"
)


def toSnakeCase(string):
    return re.sub(r"(?<=[a-z])(?=[A-Z])|[^a-zA-Z]", "_", string).upper()


association_facets_url = "http://localhost:8983/solr/association/select?wt=json&rows=0&q=*:*&facet=true&facet.field=category&facet.field=predicate"
entity_facets_url = "http://localhost:8983/solr/entity/select?wt=json&rows=0&q=*:*&facet=true&facet.field=category"
sssom_facets_url = "http://localhost:8983/solr/sssom/select?wt=json&rows=0&q=*:*&facet=true&facet.field=predicate_id"

association_facets = requests.get(association_facets_url)
entity_facets = requests.get(entity_facets_url)
sssom_facets = requests.get(sssom_facets_url)

association_categories = association_facets.json()["facet_counts"]["facet_fields"][
    "category"
]
association_predicates = association_facets.json()["facet_counts"]["facet_fields"][
    "predicate"
]
entity_categories = entity_facets.json()["facet_counts"]["facet_fields"]["category"]
mapping_predicates = sssom_facets.json()["facet_counts"]["facet_fields"]["predicate_id"]


association_category_entries = []
for category in association_categories:
    if isinstance(category, str):
        association_category_entries.append(
            f"{toSnakeCase(category.replace('biolink:', ''))} = '{category}'\n    "
        )

association_predicate_entries = []
for category in association_predicates:
    if isinstance(category, str):
        association_predicate_entries.append(
            f"{toSnakeCase(category.replace('biolink:', ''))} = '{category}'\n    "
        )

entity_category_entries = []
for category in entity_categories:
    if isinstance(category, str):
        entity_category_entries.append(
            f"{toSnakeCase(category.replace('biolink:', ''))} = '{category}'\n    "
        )

mapping_predicate_entries = []
for predicate in mapping_predicates:
    if isinstance(predicate, str):
        mapping_predicate_entries.append(
            f"{toSnakeCase(predicate.replace('skos:', ''))} = '{predicate}'\n    "
        )

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

class MappingPredicate(Enum):
    """Mapping predicates"""
    {''.join(mapping_predicate_entries)}
'''

with open(output_file, "w") as f:
    f.write(output)
