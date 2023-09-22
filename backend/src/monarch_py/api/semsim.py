from typing import List

from fastapi import APIRouter, Query
from monarch_py.api.config import oak
from monarch_py.implementations.oak.oak_implementation import SemsimSearchCategory

router = APIRouter(tags=["semsim"], responses={404: {"description": "Not Found"}})


@router.get("/compare/{subjects}/{objects}")
def _compare(
    subjects: str = "",
    objects: str = "",
):
    """Get pairwise similarity between two sets of terms

    Args:
        subjects (str, optional): List of subjects for comparison. Defaults to "".
        objects (str, optional): List of objects for comparison. Defaults to "".

    Returns:
        TermSetPairwiseSimilarity: Pairwise similarity between subjects and objects
    """
    print(
        f"""
    Running semsim compare:
        subjects: {subjects.split(',')}
        objects: {objects.split(',')}
    """
    )
    results = oak().compare(
        subjects=subjects.split(","),
        objects=objects.split(","),
    )
    return results


@router.post("/compare")
def _post_compare(
    subjects: List[str] = None,
    objects: List[str] = None,
):
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
    return oak().compare(subjects, objects)


@router.get("/search")
def _search(
    subjects: str = Query(...),
    target_group: SemsimSearchCategory = Query(...),
    limit: int = Query(default=10, ge=1, le=500),
):
    """
    Search for genes or diseases by phenotype similarity<br>

    Args:<br>
        subjects (str, optional): A comma separated list of phenotypes, genes or diseases for comparison.<br>
        Examples:
            <ul>
                <li>MONDO:0019391,</li>
                <li>MP:0010771,MP:0002169,MP:0005391,MP:0005389,MP:0005367</li>
                <li>HGNC:10848,HGNC:1101</li>
            </ul>
        <br>
        target_group (SemsimSearchCategory, optional): The target group to search for, diseases, or genes
            from a specific taxon<br>
        limit: The maximum number of results to return (default 10, maximum of 500) <br>

    """
    # TODO: subjects as an argument to this api method is consistent with compare,
    #       but obviously bizarre to have objects=subjects in the translation to oaklib
    return oak().search(objects=subjects.split(","), target_groups=[target_group], limit=limit)
