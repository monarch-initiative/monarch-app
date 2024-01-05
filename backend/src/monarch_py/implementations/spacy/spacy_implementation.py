import json
import re
from dataclasses import dataclass
from typing import List

import spacy
from monarch_py.interfaces.search_interface import SearchInterface
from monarch_py.interfaces.text_annotation_interface import TextAnnotatorInterface
from monarch_py.datamodels.model import TextAnnotationResult
from loguru import logger


@dataclass
class SpacyImplementation(TextAnnotatorInterface):
    """Implementation of Monarch Interfaces for SPACY"""

    nlp = None
    search_engine = None

    def init_spacy(self, search_engine: SearchInterface):
        self.nlp = spacy.load("en_core_sci_sm")
        self.search_engine = search_engine
        self.annotate_text("Nystagmus, strabismus, fundus, ocular albinism, lewis.")

    def annotate_text(self, text) -> List[TextAnnotationResult]:
        """Annotate text using SPACY"""
        result = ""
        try:
            entities = self.get_entities(text)
            entities = self.concatenate_same_entities(entities)
            replaced_text = self.replace_entities(text, entities)
            result += replaced_text + " "
        except IndexError as error:
            logger.error(f"Error occurred: {error}")
        result = self.convert_to_json(result)
        return result

    def get_entities(self, text):
        entities = []
        doc = self.nlp(text)
        for entity in doc.ents:
            solr_search_results = self.search_engine.search(q=str(entity))
            matches = re.findall(r"SearchResult\(id='(.*?)', category='(.*?)', name='(.*?)',", str(solr_search_results))

            filtered_results = [match for match in matches if 'obsolete' not in match[2].lower()]

            if len(filtered_results) >= 3:
                entities.extend([
                    [entity.start_char, entity.end_char, f"{filtered_results[i][2].replace(',', '')},{filtered_results[i][0]}"]
                    for i in range(3)
                ])

            for index, match in enumerate(filtered_results[3:], start=3):
                entity_lower = str.lower(str(entity))
                conditions = [
                    match[2].lower() == entity_lower + " (hpo)",
                    match[2].lower() == entity_lower,
                    match[2].lower() == entity_lower + " (mpo)"
                ]

                if any(conditions):
                    entities.append([entity.start_char, entity.end_char, f"{match[2].replace(',', '')},{match[0]}"])
        entities.sort()
        return entities

    def concatenate_same_entities(self, lst):
        result = {}
        for elem in lst:
            if len(elem) >= 3:
                key = (elem[0], elem[1])
                result[key] = result.get(key, "") + "|" + elem[2]

        return [[key[0], key[1], value] for key, value in result.items() if len(key) >= 2]

    def replace_entities(self, text, entities):
        replaced_text = text
        entities = sorted(entities, key=lambda x: x[0], reverse=True)

        for start, end, entity_data in entities:
            if 0 <= start <= len(text) and 0 <= end <= len(text):
                entity_value = f'<span class="sciCrunchAnnotation" data-sciGraph="{entity_data}">{text[start:end]}</span>'
                replaced_text = replaced_text[:start] + entity_value + replaced_text[end:]
            else:
                logger.warning(f"Indices {start} or {end} are out of range for text length {len(text)}.")

        return replaced_text

    def convert_to_json(self, text):
        result = []
        span_pattern = re.compile(r'<span class="sciCrunchAnnotation" data-sciGraph="([^"]+)">([^<]+)</span>')

        start_index = 0
        for match in span_pattern.finditer(text):
            span_data, span_text = match.group(1), match.group(2)

            if start_index < match.start():
                non_span_text = text[start_index: match.start()]
                result.append({"text": non_span_text})

            tokens = [{"id": token_parts[1], "name": token_parts[0]}
                      for token_data in span_data.split("|")
                      if (token_parts := token_data.split(",")) and len(token_parts) >= 2]

            result.append({"text": span_text, "tokens": tokens})
            start_index = match.end()

        if start_index < len(text):
            non_span_text = text[start_index:]
            result.append({"text": non_span_text})

        result.append({"text": "\n"})

        return json.loads(json.dumps(result))
