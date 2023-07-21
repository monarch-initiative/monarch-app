from dataclasses import dataclass

from oaklib.interfaces.semsim_interface import SemanticSimilarityInterface
from oaklib.datamodels.similarity import TermSetPairwiseSimilarity
from oaklib.selector import get_adapter


@dataclass
# class OakImplementation(SemanticSimilarityInterface):
class OakImplementation():
    """Implementation of Monarch Interfaces for OAK"""

    semsim = get_adapter(f"semsimian:sqlite:obo:phenio") 

    def compare(self, ts1, ts2, predicates=None, labels=False) -> TermSetPairwiseSimilarity:
        """Compare two sets of terms using OAK"""
        return self.semsim.termset_pairwise_similarity(ts1, ts2, predicates=predicates, labels=labels)
