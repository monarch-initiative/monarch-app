from fastapi import APIRouter, Depends
from models import PaginationParams

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
    pagination: PaginationParams = Depends(),
    category: str = None,
    predicate: str = None,
    subject: str = None,
    object: str = None,
    entity: str = None, # return nodes where entity is subject or object
    between: str = None # strip by comma and check associations in both directions
):
    results = get_associations(
        category=category,
        predicate=predicate,
        offset=pagination.offset,
        limit=pagination.limit,
        subject=subject,
        object=object,
        entity=entity,
        between=between
    )
    return results

@router.get("/to/{subject}")
async def _get_association_to(subject: str, pagination: PaginationParams = Depends()):
    pass

@router.get("/from/{object}")
async def _get_association_from(object: str, pagination: PaginationParams = Depends()):
    pass

@router.get("/between/{subject}/{object}")
async def _get_association_between(subject: str, object: str, pagination: PaginationParams = Depends()):
    pass

async def _get_association_find(subject_category, object_category = None):
    pass
