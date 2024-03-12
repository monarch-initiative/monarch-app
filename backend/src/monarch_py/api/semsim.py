from fastapi import APIRouter, Path, Query

from monarch_py.api.additional_models import (
    SemsimCompareRequest,
    SemsimSearchRequest,
    SemsimSearchGroup,
    SemsimMultiCompareRequest,
)
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
    ),
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


# add a multicompare post endpoint
@router.post("/multicompare")
def _post_multicompare(request: SemsimMultiCompareRequest):
    """
            Pairwise similarity between two sets of terms <br>
            <br>
            Example: <br>
        <pre>
    {
      "subjects": [ "HP:0002616", "HP:0001763", "HP:0004944", "HP:0010749", "HP:0001533", "HP:0002020", "HP:0012450", "HP:0003394", "HP:0003771", "HP:0012378", "HP:0001278", "HP:0002827",
    "HP:0002829", "HP:0002999", "HP:0003010"],
      "object_sets": [
        {
          "id": "MGI:97486",
          "label": "Pax2",
          "phenotypes": [ "MP:0003675", "MP:0003675", "MP:0003675", "MP:0011382", "MP:0011366", "MP:0010097", "MP:0012536", "MP:0003558", "MP:0004729", "MP:0009113", "MP:0006090", "MP:0001325", "MP:0001325", "MP:0006309",
    "MP:0004017", "MP:0012533", "MP:0004505", "MP:0004505", "MP:0004505"]
        },
        {
          "id": "MGI:95819",
          "label": "Grin1",
          "phenotypes": ["MP:0001435", "MP:0001405", "MP:0002797", "MP:0001386", "MP:0001901", "MP:0001901", "MP:0001901", "MP:0001901", "MP:0001901", "MP:0002906", "MP:0004811", "MP:0001900",
    "MP:0009748", "MP:0008428", "MP:0008428", "MP:0008428"]
        }
      ]
    }
        </pre>
    """
    return semsimian().multi_compare(request)


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
