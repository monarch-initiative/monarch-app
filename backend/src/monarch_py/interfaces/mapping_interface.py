from abc import ABC
from typing import List

from monarch_py.datamodels.model import MappingResults

class MappingInterface(ABC):

    def get_mappings(self,
                     entity_id: List[str] = None,
                     subject_id: List[str] = None,
                     predicate_id: List[str] = None,
                     object_id: List[str] = None,
                     mapping_justification: List[str] = None,
                     ) -> MappingResults:
        raise NotImplementedError
