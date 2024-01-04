from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from monarch_py.utils.utils import to_tsv_str
from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import solr
from monarch_py.api.additional_models import OutputFormat
from monarch_py.datamodels.model import AssociationTableResults, Node
from monarch_py.datamodels.category_enums import AssociationCategory

router = APIRouter(tags=["entity"], responses={404: {"description": "Not Found"}})


@router.get("/{id}")
async def _get_entity(
    id: str = Path(
        title="ID of the entity to retrieve",
        examples=["MONDO:0019391"],
    ),
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
) -> Union[Node, str]:
    """Retrieves the entity with the specified id

    <b>Args:</b> <br>
        id (str): ID for the entity to retrieve, ex: MONDO:0019391

    <b>Raises:</b> <br>
        HTTPException: 404 if the entity is not found

    <b>Returns:</b> <br>
        Node: Entity details for the specified id
    """
    response = solr().get_entity(id, extra=True)
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    if format == OutputFormat.json:
        return Node(**response.__dict__)  # This is an odd consequence of how Node extends Entity
    elif format == OutputFormat.tsv:
        return to_tsv_str(response)


@router.get("/{id}/{category}")
def _association_table(
    id: str = Path(
        title="ID of the entity to retrieve association table data for",
        examples=["MONDO:0019391"],
    ),
    category: AssociationCategory = Path(
        title="Type of association to retrieve association table data for",
        examples=["biolink:DiseaseToPhenotypicFeatureAssociation"],
    ),
    query: str = Query(default=None, title="query string to limit results to a subset", examples=["thumb"]),
    sort: List[str] = Query(
        default=None,
        title="Sort results by a list of field + direction statements",
        examples=["subject_label asc", "predicate asc", "object_label asc"],
    ),
    pagination: PaginationParams = Depends(),
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
) -> Union[AssociationTableResults, str]:
    """
    Retrieves association table data for a given entity and association type

    <b>Args:</b> <br>
        id (str): ID of the entity to retrieve association table data, ex: MONDO:0019391 <br>
        category (str): Category of association to retrieve association table data for, ex: biolink:DiseaseToPhenotypicFeatureAssociation <br>
        Path (str, optional): Path string to limit results to a subset. Defaults to None. <br>
        pagination (PaginationParams, optional): Pagination parameters. Defaults to Depends(). <br>

    <b>Returns:</b> <br>
        AssociationResults: Association table data for the specified entity and association type
    """
    response = solr().get_association_table(
        entity=id, category=category.value, q=query, sort=sort, offset=pagination.offset, limit=pagination.limit
    )
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        return to_tsv_str(response)
