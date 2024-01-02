from abc import ABC, abstractmethod
from typing import List
from monarch_py.datamodels.model import TextAnnotationResult


class TextAnnotatorInterface(ABC):

    def annotate_text(self, text: str) -> List[TextAnnotationResult]:
        raise NotImplementedError
