import time
from dataclasses import dataclass, asdict

from monarch_py.datamodels.model import TermSetPairwiseSimilarity
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

    def init_semsim(self):
        #    semsim = get_adapter(f"sqlite:obo:phenio")
        print("Warming up semsimian")
        start = time.time()
        self.semsim = get_adapter(f"semsimian:sqlite:obo:phenio")
        # subject_ids = ["MP:0010771", "MP:0002169", "MP:0005391", "MP:0005389", "MP:0005367"]
        # object_ids = ["HP:0004325", "HP:0000093", "MP:0006144"]
        # self.semsim.termset_pairwise_similarity(
        #     subjects=subject_ids, objects=object_ids, predicates=[IS_A, "BFO:0000050", "UPHENO:0000001"]
        # )
        print(f"Done warming up semsimian in {time.time() - start} seconds")

    def compare(
        self, subjects, objects, predicates=[IS_A, "BFO:0000050", "UPHENO:0000001"], labels=False
    ) -> TermSetPairwiseSimilarity:
        """Compare two sets of terms using OAK"""
        response = self.semsim.termset_pairwise_similarity(
            subjects=subjects,
            objects=objects,
            predicates=predicates,
            labels=labels,
        )
        return TermSetPairwiseSimilarity(**asdict(response))

    def compare_termsets(
        subjects=[""],
        objects=[""],
        predicates=[IS_A, "BFO:0000050", "UPHENO:0000001"],
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
