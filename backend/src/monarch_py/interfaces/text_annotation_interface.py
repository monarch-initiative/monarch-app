from abc import ABC
from typing import List
from monarch_py.datamodels.model import TextAnnotationResult


class TextAnnotatorInterface(ABC):
    def get_annotated_entities(self, text: str) -> List[TextAnnotationResult]:
        raise NotImplementedError

    def annotate_text(self, text: str) -> str:
        raise NotImplementedError
