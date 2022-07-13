from fastapi import APIRouter
import requests
import pysolr

from monarch_api.utils import *

router = APIRouter(
    prefix="/api/entity",
    tags=["entity"],
    responses = {
        404: {"description":"Not Found"}
    }
)

@router.get("/{id}")
async def get_entity(
        id, 
        get_association_counts: bool=False,
        ):
    url = f"{solr_url}/entity/get?id={id}"
    r = requests.get(url)
    entity = r.json()['doc']
    strip_json(entity, "_version_")

    results = entity
    
    if get_association_counts:
        association_counts = get_entity_association_counts(id)
        results["association_counts"] = association_counts

    return results
