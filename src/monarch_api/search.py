from fastapi import APIRouter, Depends
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

from monarch_api.additional_models import PaginationParams
from monarch_api.model import EntityResults

router = APIRouter(
    prefix="/api/search",
    tags=["search"],
    responses={404: {"description": "Not Found"}},
)

@router.get()
async def _search(
    q: str = "*:*",
    category: str = None,
    taxon: str = None,
    offset: int = 0,
    limit: int = 20
    ) -> EntityResults:
    """Search for entities by label, with optional filters

    Args:
        q (str, optional): _description_. Defaults to "*:*".
        category (str, optional): _description_. Defaults to None.
        taxon (str, optional): _description_. Defaults to None.
        offset (int, optional): _description_. Defaults to 0.
        limit (int, optional): _description_. Defaults to 20.

    Returns:
        EntityResults
    """
    si = SolrImplementation()
    response = si.search(
        q=q,
        category=category,
        taxon=taxon,
        ofsfet=offset,
        limit=limit
    )

    return response