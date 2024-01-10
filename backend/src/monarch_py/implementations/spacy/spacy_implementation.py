from dataclasses import dataclass
from typing import List

import spacy
from spacy.tokens.doc import Doc

from monarch_py.interfaces.search_interface import SearchInterface
from monarch_py.interfaces.text_annotation_interface import TextAnnotatorInterface
from monarch_py.datamodels.model import TextAnnotationResult, Entity


@dataclass
class SpacyImplementation(TextAnnotatorInterface):
    """Implementation of Monarch Interfaces for SPACY"""

    nlp = None
    search_engine = None

    def init_spacy(self, search_engine: SearchInterface):
        self.nlp = spacy.load("en_core_sci_sm")
        self.search_engine = search_engine
        self.annotate_text("Nystagmus, strabismus, fundus, ocular albinism, lewis.")
        self.get_annotated_entities("Ehlers-Danlos syndrome, Marfan syndrome, and Loeys-Dietz syndrome are all connective tissue disorders.")

    def get_annotated_entities(self, text) -> List[TextAnnotationResult]:
        """Annotate text using SPACY"""

        results: List[TextAnnotationResult] = []
        doc = self.nlp(text)

        #unique_entities = list(set([ent.text for ent in doc.ents]))
        #text_entities = [ent.text for ent in doc.ents]
        for entity in doc.ents:
            matching_entities = self.ground_entity(entity.text)
            result = TextAnnotationResult(text=entity.text, tokens=matching_entities, start=entity.start, end=entity.end)
            results.append(result)
        print(results)
        return results

    def annotate_text(self, text) -> str:
        """ Returns an html formatted string with tags wrapping entities found in the text """
        annotated_entities = self.get_annotated_entities(text)

        # for each annotated entity
          # relpace text with contents from create_span

        pass

    def create_span(self, entity: Entity) -> str:
        """ Returns an html formatted string with tags wrapping entities found in the text """
        pass

    def ground_entity(self, entity_text: str) -> List[Entity]:
        returned_entities = []

        search_results = self.search_engine.search(q=str(entity_text))
        filtered_search_results = [result for result in search_results.items if not result.deprecated]

        returned_entities = filtered_search_results[:3]

        for result in filtered_search_results[3:]:
            stripped_result_name = result.name.lower().replace(" (hpo)", "").replace(" (mpo)", "")
            if entity_text.lower() == stripped_result_name:
                returned_entities.append(result)

        return returned_entities


