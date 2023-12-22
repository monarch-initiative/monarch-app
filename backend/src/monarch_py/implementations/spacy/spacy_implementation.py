import json
import re
from dataclasses import dataclass
from typing import List

import requests
import spacy
from loguru import logger


from monarch_py.interfaces.search_interface import SearchInterface
from monarch_py.interfaces.text_annotation_interface import TextAnnotatorInterface
from monarch_py.datamodels.model import AnnotatedJSONResult
from oaklib.interfaces.semsim_interface import SemanticSimilarityInterface
from oaklib.selector import get_adapter
from linkml_runtime.dumpers.json_dumper import JSONDumper
import pystow

@dataclass
class SpacyImplementation(TextAnnotatorInterface):
    """Implementation of Monarch Interfaces for SPACY"""

    nlp = None
    search_engine = None

    def init_spacy(self, search_engine: SearchInterface):
        self.nlp = spacy.load("en_core_sci_sm")
        self.search_engine = search_engine
        # TODO: remove this print, it's just there to confirm that search works from here
        # print(search_engine.search(q="ehlers"))
        self.annotate_text("Nystagmus, strabismus and fundus.")

    def annotate_text(self, text) -> List[AnnotatedJSONResult]:
        """Annotate text using SPACY"""
        result = ""
        entities = []
        doc = self.nlp(text)
        try:
            entities = self.get_monarch_equivalent(doc, entities)
            entities = self.get_monarch_top_three(doc, entities)
            entities.sort()
            entities = self.concatenate_same_entities(entities)
            replaced_text = self.replace_entities(text, entities)
            result += replaced_text + " "
        except IndexError as error:
            # Handling the list index out of range error
            print("Error occurred:", error)

        result = self.convert_to_json(result)
        #print(result)
        return result

    def search_monarch_api(self, query):
        try:
            url = f"https://api-dev.monarchinitiative.org/v3/api/search?q={query}&limit=20&offset=0"
            # url = f"https://127.0.0.1:8000/v3/api/search?q={query}&limit=20&offset=0" #alternate DEV or PROD/v3 urls
            response = requests.get(url)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"Error in Monarch Initiative API request: {e}")
            raise
        except Exception as e:
            print(f"Error processing Monarch Initiative API response: {e}")
            raise

    def get_monarch_equivalent(self, doc, entities):
        for entity in doc.ents:
            res_j = self.search_monarch_api(entity)
            for t in range(len(res_j['items'])):
                item_name = str.lower(res_j['items'][t]['name'])
                entity_lower = str.lower(str(entity))

                conditions = [
                    item_name == entity_lower + " (hpo)",
                    item_name == entity_lower,
                    item_name == entity_lower + " (mpo)"
                ]

                if any(conditions):
                    element = [entity.start_char, entity.end_char,
                               res_j['items'][t]['name'] + "," + res_j['items'][t]['id']]
                    entities.append(element)
        return entities

    def get_monarch_top_three(self, doc, entities):
        for entity in doc.ents:
            for sublist in entities:
                if str(entity).lower() not in sublist[2].lower():
                    res_j = self.search_monarch_api(entity)
                    if len(res_j['items']) > 3:
                        for t in range(3):
                            element = [entity.start_char, entity.end_char,
                                       res_j['items'][t]['name'] + "," + res_j['items'][t]['id']]
                            entities.append(element)
                    break
        return entities

    def concatenate_same_entities(self, lst):
        result = {}
        for elem in lst:
            key = (elem[0], elem[1])
            if key in result:
                result[key] += "|" + elem[2]
            else:
                result[key] = elem[2]
        concatenated_list = [[key[0], key[1], value] for key, value in result.items()]
        return concatenated_list

    def replace_entities(self, text, entities):
        replaced_text = text
        entities = sorted(entities, key=lambda x: x[0], reverse=True)
        for entity in entities:
            start, end = entity[0], entity[1]
            entity_value = f'<span class="sciCrunchAnnotation" data-sciGraph="{entity[2]}">{text[start:end]}</span>'
            replaced_text = replaced_text[:start] + entity_value + replaced_text[end:]
        return replaced_text

    def convert_to_json(self, text):
        result = []
        span_pattern = re.compile(r'<span class="sciCrunchAnnotation" data-sciGraph="([^"]+)">([^<]+)</span>')

        start_index = 0
        for match in span_pattern.finditer(text):
            span_data = match.group(1)
            span_text = match.group(2)

            if start_index < match.start():
                non_span_text = text[start_index: match.start()]
                result.append({"text": non_span_text})

            tokens = []
            for token_data in span_data.split("|"):
                token_parts = token_data.split(",")
                tokens.append({"id": token_parts[1], "name": token_parts[0]})

            result.append({"text": span_text, "tokens": tokens})
            start_index = match.end()

        if start_index < len(text):
            non_span_text = text[start_index:]
            result.append({"text": non_span_text})

        result.append({"text": "\n"})

        api_response = json.dumps(result)
        data = json.loads(api_response)

        return data
