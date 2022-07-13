from fastapi import APIRouter

from monarch_api.utils.helper import *
from monarch_api.utils.entity import *

router = APIRouter(
    prefix="/api/entity",
    tags=["entity"],
    responses = {
        404: {"description":"Not Found"}
    }
)

@router.get("/{id}")
async def _get_entity(
        id, 
        get_association_counts: bool=False,
        ):

    results = get_entity(id, get_association_counts)
    return results

