from fastapi import APIRouter
import requests
import pysolr

from monarch_api.utils import *

router = APIRouter(
    prefix="/api/association",
    tags=["association"],
    responses = {
        404: {"description":"Not Found"}
    }
)

@router.get("/{id}")
async def test(
        id, 
        ):
    url = f"{solr_url}/association/get?id={id}"
    r = requests.get(url)
    association = r.json()['doc']
    results = {"association": association}
    
    return results
