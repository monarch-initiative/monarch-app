import requests, collections

solr_url = "http://localhost:8983/solr"
association_url = "http://localhost:8983/solr/association"


def get_filtered_facet(entity_id, filter_field, facet_field):
    response = requests.get(f"{association_url}/select?q=*:*&rows=0&facet=true&facet.field={facet_field}&fq={filter_field}:\"{entity_id}\"")
    facet_fields = response.json()["facet_counts"]["facet_fields"][facet_field]
    
    return dict(zip(facet_fields[::2], facet_fields[1::2]))

def get_entity_association_counts(entity_id):
    object_categories = get_filtered_facet(entity_id, filter_field="subject", facet_field="object_category")
    subject_categories = get_filtered_facet(entity_id, filter_field="object", facet_field="subject_category")
    categories = collections.Counter(object_categories) + collections.Counter(subject_categories)
    return categories