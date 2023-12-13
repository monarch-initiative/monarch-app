import re
import time
from dataclasses import dataclass
from typing import List

from oaklib.interfaces.semsim_interface import SemanticSimilarityInterface
from oaklib.selector import get_adapter
from linkml_runtime.dumpers.json_dumper import JSONDumper
from loguru import logger
import pystow

from monarch_py.datamodels.model import TermSetPairwiseSimilarity
from monarch_py.implementations.oak.annotation_utils import (
    get_word_length,
    concatenate_same_entities,
    concatenate_ngram_entities,
    replace_entities,
    convert_to_json,
)


@dataclass
class OakImplementation(SemanticSimilarityInterface):
    """Implementation of Monarch Interfaces for OAK"""

    semsim = None
    json_dumper = JSONDumper()
    default_predicates = ["rdfs:subClassOf", "BFO:0000050", "UPHENO:0000001"]

    default_phenio_db_url = "https://data.monarchinitiative.org/monarch-kg-dev/latest/phenio.db.gz"
    phenio_adapter = None

    def init_phenio_adapter(self, phenio_path: str = None, force_update: bool = False):
        if self.phenio_adapter is None:
            logger.info("Warming up semsimian")
            start = time.time()
            # self.phenio_adapter = get_adapter(f"sqlite:obo:phenio")

            if phenio_path:
                logger.debug(f"Creating phenio adapter using phenio_path at {phenio_path}")
                self.phenio_adapter = get_adapter(f"sqlite:{phenio_path}")
            else:
                monarchstow = pystow.module("monarch")

                with monarchstow.ensure_gunzip(
                    "phenio", url=self.default_phenio_db_url, force=force_update
                ) as stowed_phenio_path:
                    logger.debug(f"Creating phenio adapter using pystow at {stowed_phenio_path}")
                    self.phenio_adapter = get_adapter(f"sqlite:{stowed_phenio_path}")

            # run a query to get the adapter to initialize properly
            logger.debug("Running query to initialize adapter")

            # TODO: run a little bit of text annotation here to get oak warmed up
            print("Oaklib adapter warmup")
            for ann in self.phenio_adapter.annotate_text("Nystagmus, strabismus and fundus."):
                print(ann.subject_start, ann.subject_end, ann.object_id, ann.object_label)

            logger.info(f"Phenio adapter ready, warmup time: {time.time() - start} sec")
            return self

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
        response = self.semsim.termset_pairwise_similarity(  # type: ignore
            subjects=subjects,
            objects=objects,
            predicates=predicates,
            labels=labels,
        )
        logger.debug(f"Comparison took: {time.time() - compare_time} sec")

        response_dict = self.json_dumper.to_dict(response)
        return TermSetPairwiseSimilarity(**response_dict)

    def annotate_text(self, text):
        """Annotate text using OAK"""
        paragraphs = text.split("\n")
        paragraphs_annotated = []
        for paragraph in paragraphs:
            result = ""
            sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", paragraph)
            for sentence in sentences:
                entities = []
                for ann in self.phenio_adapter.annotate_text(sentence):  # type: ignore
                    if len(ann.object_label) >= 4:
                        element = [ann.subject_start, ann.subject_end, str(ann.object_label) + "," + str(ann.object_id)]
                        if (get_word_length(sentence, ann.subject_start - 1) - len(ann.object_label)) < 2:
                            entities.append(element)
                try:
                    entities.sort()
                    entities = concatenate_same_entities(entities)
                    entities = concatenate_ngram_entities(entities)
                    replaced_text = replace_entities(sentence, entities)
                    result += replaced_text + " "
                except IndexError as error:
                    # Handling the list index out of range error
                    result += sentence + " "
                    print("Error occurred:", error)

            paragraphs_annotated.append(result)
        result = convert_to_json(paragraphs_annotated)
        return result
