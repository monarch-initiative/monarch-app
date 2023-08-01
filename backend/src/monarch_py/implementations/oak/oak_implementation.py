import time
from dataclasses import dataclass, asdict

from loguru import logger

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
class OakImplementation(SemanticSimilarityInterface):
    """Implementation of Monarch Interfaces for OAK"""

    semsim: SemanticSimilarityInterface = None # or is it a SqlImplementation?
    
    def init_semsim(self):
        if self.semsim is None:
            logger.info("Warming up semsimian")
            start = time.time()
            # self.semsim = get_adapter(f"sqlite:obo:phenio")
            logger.debug("Getting semsimian adapter")
            self.semsim = get_adapter(f"semsimian:sqlite:obo:phenio")

            # for some reason, we need to run a query to get the adapter
            # to initialize properly
            logger.debug("Running query to initialize adapter")
            self.semsim.termset_pairwise_similarity(
                subjects=["MP:0010771"],
                objects=["HP:0004325"],
                predicates=[IS_A, "BFO:0000050", "UPHENO:0000001"],
                labels=False,
            )
            logger.info(f"Semsimian ready, warmup time: {time.time() - start} sec")
            return self

    def compare(
        self, subjects, objects, predicates=[IS_A, "BFO:0000050", "UPHENO:0000001"], labels=False
    ) -> TermSetPairwiseSimilarity:
        """Compare two sets of terms using OAK"""
        try: 
            return self.semsim.termset_pairwise_similarity(
                subjects=subjects,
                objects=objects,
                predicates=predicates,
                labels=labels,
            )
        except AttributeError:
            self.init_semsim()
            return self.semsim.termset_pairwise_similarity(
                subjects=subjects,
                objects=objects,
                predicates=predicates,
                labels=labels,
            )
