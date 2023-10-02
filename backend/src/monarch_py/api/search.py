from typing import List, Union

from fastapi import APIRouter, Depends, Query

from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import solr
from monarch_py.datamodels.model import SearchResults

router = APIRouter(
    tags=["search"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/search")
async def search(
    q: str = Query(default=None),
    category: Union[List[str], None] = Query(default=None),
    in_taxon_label: Union[List[str], None] = Query(default=None),
    pagination: PaginationParams = Depends(),
) -> SearchResults:
    """Search for entities by label, with optional filters

    Args:
        q (str, optional): Query string. Defaults to "*:*".
        category (str, optional): Filter by biolink model category. Defaults to None.
        in_taxon_label (str, optional): Filter by taxon label. Defaults to None.
        offset (int, optional): Offset for pagination. Defaults to 0.
        limit (int, optional): Limit results. Defaults to 20.

    Returns:
        EntityResults
    """
    facet_fields = ["category", "in_taxon_label"]
    response = solr().search(
        q=q or "*:*",
        category=category,
        in_taxon_label=in_taxon_label,
        facet_fields=facet_fields,
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return response


@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(
        default="*:*",
        title="Query string to autocomplete against",
        examples=["fanc", "ehler"],
    )
) -> SearchResults:
    """Autocomplete for entities by label

    Args:
        q (str): Query string to autocomplete against

    Returns:
        SearchResults
    """
    response = solr().autocomplete(q=q)
    return response
