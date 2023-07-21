from dataclasses import dataclass

from oaklib.datamodels.similarity import TermSetPairwiseSimilarity
from oaklib.interfaces.semsim_interface import SemanticSimilarityInterface
from oaklib.selector import get_adapter
# these imports are from get_similarity.py
import oaklib.datamodels.ontology_metadata as omd
from oaklib import OntologyResource
from oaklib.constants import OAKLIB_MODULE
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation

HP_DB_URL = "https://s3.amazonaws.com/bbop-sqlite/hp.db.gz"
IS_A = omd.slots.subClassOf.curie


@dataclass
# class OakImplementation(SemanticSimilarityInterface):
class OakImplementation(SemanticSimilarityInterface):
    """Implementation of Monarch Interfaces for OAK"""

    semsim = get_adapter(f"sqlite:obo:phenio")
    # semsim = get_adapter(f"semsimian:sqlite:obo:phenio")

    def compare(self, subjects, objects, predicates=None, labels=False) -> TermSetPairwiseSimilarity:
        """Compare two sets of terms using OAK"""
        return self.semsim.termset_pairwise_similarity(
            subjects=subjects,
            objects=objects,
            predicates=predicates,
            labels=labels,
        )

    def compare_termsets(
        subjects=[""],
        objects=[""],
        predicates=[IS_A, "BFO:0000050"],
        offset: int = 0,
        limit: int = 20,
    ):
        """Get pairwise similarity between two sets of terms
        
        This is from utils/get_similarity.py, not sure what the difference is between this and compare() above
        """
        hp_db = OAKLIB_MODULE.ensure_gunzip(url=HP_DB_URL, autoclean=False)
        oi = SqlImplementation(OntologyResource(slug=hp_db))
        results = oi.termset_pairwise_similarity(subjects, objects, predicates)
        return results
