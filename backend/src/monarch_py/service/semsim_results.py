"""Backend-independent shaping of semsim search results.

Both backends return `SemsimSearchResult`s with a full `similarity` payload. The fields added
here are derived from that payload, so they mean the same thing whichever backend served the
request.
"""

from typing import List, Optional

from monarch_py.datamodels.model import SemsimSearchResult, SemsimSearchSettings, TermSetPairwiseSimilarity


def _mean_best_match_score(matches) -> float:
    """Mean score over one side's best matches. A term with no match scores 0, as in the ranking."""
    scores = [match.score for match in (matches or {}).values()]
    return sum(scores) / len(scores) if scores else 0.0


def direction_scores(similarity: Optional[TermSetPairwiseSimilarity]) -> tuple:
    """(subject_to_object, object_to_subject) averages of a termset comparison.

    These are the two halves the search score combines: subject_to_object ranks by one of them,
    object_to_subject by the other, and bidirectional by their mean.
    """
    if similarity is None:
        return None, None
    return (
        _mean_best_match_score(similarity.subject_best_matches),
        _mean_best_match_score(similarity.object_best_matches),
    )


def annotate_search_results(results, settings: SemsimSearchSettings) -> List[SemsimSearchResult]:
    """Attach both direction scores and the settings the search ran with to every result."""
    annotated = []
    for result in results or []:
        result.subject_to_object_score, result.object_to_subject_score = direction_scores(result.similarity)
        result.search_settings = settings
        annotated.append(result)
    return annotated
