from dataclasses import dataclass
# from typing import Iterable, List

from oaklib.interfaces.semsim_interface import SemanticSimilarityInterface
from oaklib.selector import get_adapter


@dataclass
class OakImplementation(SemanticSimilarityInterface):
    """Implementation of Monarch Interfaces for OAK
    Notes:
        - This is an in-progress conversion to OAK
        - Biolink-API call args:
            - reference_ids -> subject_ids
            - query_ids -> object_ids
            - is_feature_set = ??
    """
    oi = get_adapter(f"sqlite:obo:phenio") 


    def termset_pairwise_similarity(self, ts1, ts2, predicates=None, labels=False) -> float:
        tsps = self.oi.termset_pairwise_similarity(ts1, ts2, predicates=predicates, labels=labels)

        average_score = tsps["average_score"]
        best_score = tsps["best_score"]
        subject_termset = tsps["subject_termset"]
        object_termset = tsps["object_termset"]
        subject_best_matches = tsps["subject_best_matches"]
        object_best_matches = tsps["object_best_matches"]

        return tsps

