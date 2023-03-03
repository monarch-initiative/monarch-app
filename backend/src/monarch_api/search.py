from fastapi import APIRouter#, Depends

from monarch_py.implementations.solr.solr_implementation import SolrImplementation

from monarch_api.config import settings
from monarch_api.model import EntityResults


router = APIRouter(
    prefix="/api",
    tags=["search"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/search")
async def search(
    q: str = "*:*",
    category: str = None,
    taxon: str = None,
    offset: int = 0,
    limit: int = 20
    ) -> EntityResults:
    """Search for entities by label, with optional filters

    Args:
        q (str, optional): TODO. Defaults to "*:*".
        category (str, optional): TODO. Defaults to None.
        taxon (str, optional): TODO. Defaults to None.
        offset (int, optional): Offset for pagination. Defaults to 0.
        limit (int, optional): Limit results. Defaults to 20.

    Returns:
        EntityResults
    """
    si = SolrImplementation(base_url=settings.solr_url)
    response = si.search(
        q=q,
        category=category,
        taxon=taxon,
        ofsfet=offset,
        limit=limit
    )

    return response
