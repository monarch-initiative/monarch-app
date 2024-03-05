from fastapi import APIRouter, Path, Query
from typing import List

from monarch_py.api.additional_models import SemsimCompareRequest, SemsimSearchRequest, SemsimSearchGroup
from monarch_py.api.config import semsimian, solr
from monarch_py.api.utils.similarity_utils import parse_similarity_prefix
from monarch_py.datamodels.category_enums import AssociationPredicate, EntityCategory
from monarch_py.datamodels.model import SearchResults

router = APIRouter(tags=["semsim"], responses={404: {"description": "Not Found"}})


@router.get("/autocomplete")
def autocomplete(
    q: str = Query(
        default="*:*",
        title="Query string to autocomplete against",
        examples=["fanc", "ehler"],
    )
) -> SearchResults:
    """
    Autocomplete for semantic similarity lookups, prioritizes entities which have direct phenotype associations.
    Note: This API endpoint is experimental and may evolve or disappear over time.

    Args:
        q (str): Query string to autocomplete against

    Returns:
        SearchResults
    """
    response = solr().autocomplete(
        q=q,
        category=[EntityCategory.DISEASE, EntityCategory.GENE, EntityCategory.PHENOTYPIC_FEATURE],
        prioritized_predicates=[AssociationPredicate.HAS_PHENOTYPE],
    )
    return response


@router.get("/compare/{subjects}/{objects}")
def _compare(
    subjects: str = Path(..., title="List of subjects for comparison"),
    objects: str = Path(..., title="List of objects for comparison"),
):
    """Get pairwise similarity between two sets of terms

    <b>Args:</b> <br>
        subjects (str, optional): List of subjects for comparison. Defaults to "". <br>
        objects (str, optional): List of objects for comparison. Defaults to "". <br>

    <b>Returns:</b> <br>
        TermSetPairwiseSimilarity: Pairwise similarity between subjects and objects
    """
    print(
        f"""
    Running semsim compare:
        subjects: {subjects.split(',')}
        objects: {objects.split(',')}
    """
    )
    results = semsimian().compare(
        subjects=subjects.split(","),
        objects=objects.split(","),
    )
    return results


@router.post("/compare")
def _post_compare(request: SemsimCompareRequest):
    """
        Pairwise similarity between two sets of terms <br>
        <br>
        Example: <br>
    <pre>
    {
      "subjects": ["MP:0010771","MP:0002169","MP:0005391","MP:0005389","MP:0005367"],
      "objects": ["HP:0004325","HP:0000093","MP:0006144"]
    }
    </pre>
    """
    return semsimian().compare(subjects=request.subjects, objects=request.objects)


# Do we like /multicompare/HP:212,HP:443?objects=HP:123,HP:456&objects=HP:789,HP:101112 ?
@router.get("/multicompare/{subjects}")
def _multicompare(
    subjects: str = Path(..., title="Comma separated list of subjects for comparison"),
    objects: List[str] = Query(..., title="List of comma separated object sets to compare against"),
):

    return semsimian().multi_compare(subjects=subjects.split(","), object_sets=[obj.split(",") for obj in objects])


@router.get("/search/{termset}/{group}")
def _search(
    termset: str = Path(..., title="Termset to search"),
    group: SemsimSearchGroup = Path(..., title="Group of entities to search within (e.g. Human Genes)"),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Search for terms in a termset

    <b>Args:</b> <br>
        termset (str, optional): Comma separated list of term IDs to find matches for. <br>
        group (str, optional): Group of entities to search within (e.g. Human Genes) <br>
        limit (int, optional): Limit the number of results. Defaults to 10.

    <b>Returns:</b> <br>
        List[str]: List of matching terms
    """
    terms = [term.strip() for term in termset.split(",")]
    results = semsimian().search(termset=terms, prefix=parse_similarity_prefix(group), limit=limit)
    return results


@router.post("/search")
def _post_search(request: SemsimSearchRequest):
    """
        Search for terms in a termset <br>
        <br>
        Example: <br>
    <pre>
    {
      "termset": ["HP:0002104", "HP:0012378", "HP:0012378", "HP:0012378"],
      "group": "Human Diseases",
      "limit": 5
    }
    </pre>
    """
    return semsimian().search(
        termset=request.termset, prefix=parse_similarity_prefix(request.group.value), limit=request.limit
    )
