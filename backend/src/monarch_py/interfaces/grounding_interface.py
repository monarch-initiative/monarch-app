from abc import ABC
from typing import List

from monarch_py.datamodels.model import Entity


class GroundingInterface(ABC):
    """Abstract interface for grounding text to entities"""

    def ground_entity(self, text: str) -> List[Entity]:
        """
        Grounds a single entity

        Args:
            text (str): Text to ground
        Returns:
            Entity: Dataclass representing a single entity
        """

        raise NotImplementedError
