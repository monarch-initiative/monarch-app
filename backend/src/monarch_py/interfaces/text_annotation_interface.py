from abc import ABC, abstractmethod
from typing import List
from monarch_py.datamodels.model import AnnotatedJSONResult


class TextAnnotatorInterface(ABC):

    def annotate_text(self, text: str) -> List[AnnotatedJSONResult]:
        raise NotImplementedError
