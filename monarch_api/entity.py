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
async def test(
        id, 
        fetch_objects: bool=False,
        get_association_counts: bool=False,
        unselect_evidence: bool=False,
        exclude_automatic_assertions: bool=False,
        use_compact_associations: bool=False,
        rows: int=None
        ):
    url = f"{solr_url}/entity/get?id={id}"
    r = requests.get(url)
    entity = r.json()['doc']
    results = {"entity": entity}
    
    if get_association_counts:
        association_counts = get_entity_association_counts(id)
        results["association_counts"] = association_counts

    return results
