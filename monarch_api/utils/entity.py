import requests

from monarch_api.utils.helper import *

def get_entity(id, get_association_counts: bool = False):
    url = f"{solr_url}/entity/get?id={id}"
    r = requests.get(url)
    entity = r.json()['doc']
    strip_json(entity, "_version_")

    if get_association_counts:
        association_counts = get_entity_association_counts(id)
        entity["association_counts"] = association_counts

    return entity

