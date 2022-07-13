from fastapi import APIRouter
import requests
import pysolr

from monarch_api.utils.helper import *
from monarch_api.utils.association import *

router = APIRouter(
    prefix="/api/association",
    tags=["association"],
    responses = {
        404: {"description":"Not Found"}
    }
)

@router.get("/all")
async def _get_all_associations(
    category: str = None,
    predicate: str = None,
    offset: int = 0,
    limit: int = 20,
    subject: str = None,
    object: str = None,
    entity: str = None, # return nodes where entity is subject or object
    between: str = None # strip by comma and check associations in both directions
):
    results = get_associations(
        category=category,
        predicate=predicate,
        offset=offset,
        limit=limit,
        subject=subject,
        object=object,
        entity=entity,
        between=between
    )
    return results

@router.get("/to/{subject}")
async def _get_association_to(subject):
    pass

@router.get("/from/{object}")
async def _get_association_from(object):
    pass

@router.get("/between/{subject}/{object}")
async def _get_association_between(subject, object):
    pass

async def _get_association_find(subject_category, object_category = None):
    pass
