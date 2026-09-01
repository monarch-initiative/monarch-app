from abc import ABC
from typing import List, Optional

from monarch_py.datamodels.model import Entity


class GroundingInterface(ABC):
    """Abstract interface for grounding text to entities"""

    def ground_entity(
        self,
        text: str,
        prefix: Optional[List[str]] = None,
        category: Optional[List[str]] = None,
    ) -> List[Entity]:
        """
        Grounds a single entity

        Args:
            text (str): Text to ground
            prefix (List[str], optional): Restrict results to entities whose identifier
                uses one of these CURIE prefixes (e.g. ["MONDO", "HP"]). Defaults to None.
            category (List[str], optional): Restrict results to entities of one of these
                biolink categories (e.g. ["biolink:Disease"]). Defaults to None.
        Returns:
            Entity: Dataclass representing a single entity
        """

        raise NotImplementedError
