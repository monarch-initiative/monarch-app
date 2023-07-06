from abc import ABC, abstractmethod

from monarch_py.datamodels.model import Entity


class EntityInterface(ABC):
    """Abstract interface for entities in the Monarch KG"""

    @abstractmethod
    def get_entity(self, id: str, get_association_counts: bool = False, get_hierarchy: bool = False) -> Entity:
        """Retrieve a specific entity by exact ID match, with optional extras

        Args:
            id (str): id of the entity to search for.
            get_association_counts (bool, optional): Whether to get a count of associations for the entity. Defaults to False.
            get_hierarchy (bool, optional): Whether to get the entity's heirarchy in the data model. Defaults to False.

        Raises:
            NotImplementedError: Use a specific implementation (see the documentation for a list of implementations)

        Returns:
            Entity: Dataclass representing results of an entity search.
        """
        raise NotImplementedError
