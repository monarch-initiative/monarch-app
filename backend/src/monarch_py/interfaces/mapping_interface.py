from abc import ABC
from typing import List

from monarch_py.datamodels.model import MappingResults


class MappingInterface(ABC):
    def get_mappings(
        self,
        entity_id: List[str] = None,
        subject_id: List[str] = None,
        predicate_id: List[str] = None,
        object_id: List[str] = None,
        mapping_justification: List[str] = None,
    ) -> MappingResults:
        """
        Get SSSOM Mappings based on the provided constraints

        Args:
            entity_id: Filter to only mappings matching the specified entity IDs. Defaults to None.
            subject_id: Filter to only mappings matching the specified subject IDs. Defaults to None.
            predicate_id: Filter to only mappings matching the specified predicate IDs. Defaults to None.
            object_id: Filter to only mappings matching the specified object IDs. Defaults to None.
            mapping_justification: Filter to only mappings matching the specified mapping justifications. Defaults to None.
        """
        raise NotImplementedError
