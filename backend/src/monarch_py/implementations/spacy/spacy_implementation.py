import re
import time
from dataclasses import dataclass
from typing import List

from oaklib.interfaces.semsim_interface import SemanticSimilarityInterface
from oaklib.selector import get_adapter
from linkml_runtime.dumpers.json_dumper import JSONDumper
from loguru import logger
import pystow

import spacy

from monarch_py.implementations.spacy.text_annotation_utils import (
    concatenate_same_entities,
    replace_entities,
    convert_to_json,
    get_monarch_equivalent,
    get_monarch_top_three,
)
from monarch_py.interfaces.search_interface import SearchInterface


@dataclass
class SpacyImplementation():
    """Implementation of Monarch Interfaces for SPACY"""

    nlp = None
    search_engine = None

    def init_spacy(self, search_engine: SearchInterface):
        self.nlp = spacy.load("en_core_sci_sm")
        self.search_engine = search_engine
        # TODO: remove this print, it's just there to confirm that search works from here
        print(search_engine.search(q="ehlers"))
        self.annotate_text("Nystagmus, strabismus and fundus.")

    def annotate_text(self, text):
        """Annotate text using SPACY"""
        result = ""
        entities = []
        doc = self.nlp(text)
        try:
            entities = get_monarch_equivalent(doc, entities)
            entities = get_monarch_top_three(doc, entities)
            entities.sort()
            entities = concatenate_same_entities(entities)
            #    entities = concatenate_ngram_entities(entities)
            replaced_text = replace_entities(text, entities)
            result += replaced_text + " "
        except IndexError as error:
            # Handling the list index out of range error
            print("Error occurred:", error)

        result = convert_to_json(result)
        return result

