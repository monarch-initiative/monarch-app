from io import StringIO
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.responses import StreamingResponse

from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import solr
from monarch_py.api.additional_models import OutputFormat
from monarch_py.datamodels.category_enums import AssociationCategory
from monarch_py.datamodels.model import AssociationTableResults, Node
from monarch_py.utils.association_type_utils import AssociationTypeMappings
from monarch_py.utils.format_utils import to_json, to_tsv

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
        tsv = ""
        for row in to_tsv(response, print_output=False):
            tsv += row
        return Response(content=tsv, media_type="text/tab-separated-values")


def _validated_section_key(category: str) -> str:
    """Reject a section key that names neither a configured section nor a biolink category.

    The path param can no longer be the `AssociationCategory` enum, because a section key
    may be a free-form string (`drug_indications`) rather than a category. Validating
    against the known keys restores what the enum used to give us: an unknown value fails
    loudly instead of reaching Solr. Without this, `category` is interpolated into a filter
    query where `escape()` only escapes `:` — so `/entity/{id}/*` becomes `category:*` and
    returns the entity's associations across every category, and a value containing a space
    or quote produces a malformed fq and a 500.
    """
    if AssociationTypeMappings.get_mapping_by_key(category):
        return category
    try:
        return AssociationCategory(category).value
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unknown association-type section key {category!r}. Expected a configured "
                f"section key or a biolink association category."
            ),
        )


@router.get("/{id}/{category}")
def _association_table(
    id: str = Path(
        title="ID of the entity to retrieve association table data for",
        examples=["MONDO:0019391"],
    ),
    category: str = Path(
        title="Association-type section key (an AssociationTypeMapping key). For plain "
        "single-category sections this is the biolink association category.",
        examples=["biolink:DiseaseToPhenotypicFeatureAssociation"],
    ),
    query: str = Query(default=None, title="query string to limit results to a subset", examples=["thumb"]),
    traverse_orthologs: bool = Query(
        default=False,
        title="Traverse orthologs to get associations",
        examples=[True, False],
    ),
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
    download: bool = Query(
        default=False,
        title="Download the results as a file",
        examples=[True, False],
    ),
    direct: bool = Query(
        default=False,
        title="Only return direct associations",
        examples=[True, False],
    ),
    facet_fields: List[str] = Query(
        default=None,
        title="Facet fields to include in the response",
        examples=["subject", "subject_taxon", "predicate"],
    ),
    facet_queries: List[str] = Query(
        default=None, title="Facet queries to include in the response", examples=['subject_category:"biolink:Gene"']
    ),
    filter_queries: List[str] = Query(
        default=None, title="Filter queries to limit the response", examples=['subject_category:"biolink:Gene"']
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
        entity=id,
        category=_validated_section_key(category),
        q=query,
        traverse_orthologs=traverse_orthologs,
        direct=direct,
        facet_fields=facet_fields,
        facet_queries=facet_queries,
        filter_queries=filter_queries,
        sort=sort,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    if download is True:
        string_response = (
            to_tsv(response, print_output=False)
            if format == OutputFormat.tsv
            else to_json(response, print_output=False)
        )
        stream = StringIO(string_response)
        response = StreamingResponse(
            stream, media_type="text/tab-separated-values" if format == OutputFormat.tsv else "application/json"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=assoc-table-{id}.{format.value}"
        return response
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        tsv = ""
        for row in to_tsv(response, print_output=False):
            tsv += row
        return Response(content=tsv, media_type="text/tab-separated-values")
