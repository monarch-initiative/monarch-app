import time
from dataclasses import dataclass
from typing import List

from loguru import logger

from monarch_py.datamodels.model import TermSetPairwiseSimilarity
from oaklib.interfaces.semsim_interface import SemanticSimilarityInterface
from oaklib.selector import get_adapter
from linkml_runtime.dumpers.json_dumper import JSONDumper
import pystow


@dataclass
class OakImplementation(SemanticSimilarityInterface):
    """Implementation of Monarch Interfaces for OAK"""

    semsim = None
    json_dumper = JSONDumper()
    default_predicates = ["rdfs:subClassOf", "BFO:0000050", "UPHENO:0000001"]

    default_phenio_db_url = "https://data.monarchinitiative.org/monarch-kg-dev/latest/phenio.db.gz"

    def init_semsim(self, phenio_path: str = None, force_update: bool = False):
        if self.semsim is None:
            logger.info("Warming up semsimian")
            start = time.time()
            # self.semsim = get_adapter(f"sqlite:obo:phenio")


            if phenio_path:
                logger.debug(f"Creating semsimian adapter using phenio_path at {phenio_path}")
                self.semsim = get_adapter(f"semsimian:sqlite:{phenio_path}")
            else:
                monarchstow = pystow.module("monarch")

                with monarchstow.ensure_gunzip(
                    "phenio", url=self.default_phenio_db_url, force=force_update
                ) as stowed_phenio_path:
                    logger.debug(f"Creating semsimian adapter using pystow at {stowed_phenio_path}")
                    self.semsim = get_adapter(f"semsimian:sqlite:{stowed_phenio_path}")

            # run a query to get the adapter to initialize properly
            logger.debug("Running query to initialize adapter")
            self.semsim.termset_pairwise_similarity(
                subjects=["MP:0010771"],
                objects=["HP:0004325"],
                predicates=self.default_predicates,
                labels=False,
            )
            logger.info(f"Semsimian ready, warmup time: {time.time() - start} sec")
            return self

    def compare(
        self, subjects: List[str], objects: List[str], predicates: List[str] = None, labels=False
    ) -> TermSetPairwiseSimilarity:
        """Compare two sets of terms using OAK"""
        predicates = predicates or self.default_predicates
        logger.debug(f"Comparing {subjects} to {objects} using {predicates}")
        compare_time = time.time()
        response = self.semsim.termset_pairwise_similarity(
            subjects=subjects,
            objects=objects,
            predicates=predicates,
            labels=labels,
        )
        logger.debug(f"Comparison took: {time.time() - compare_time} sec")

        response_dict = self.json_dumper.to_dict(response)
        return TermSetPairwiseSimilarity(**response_dict)
