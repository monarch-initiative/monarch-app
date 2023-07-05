from abc import ABC, abstractmethod
from typing import List

from monarch_py.datamodels.model import AssociationResults


class AssociationInterface(ABC):
    """Abstract interface for associations in the Monarch KG"""

    @abstractmethod
    def get_associations(
        self,
        category: List[str] = None,
        subject: List[str] = None,
        predicate: List[str] = None,
        subject_closure: str = None,
        object: List[str] = None,
        object_closure: str = None,
        entity: List[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> AssociationResults:
        """Retrieve paginated association records, with filter options

        Args:
            category (str, optional): Filter to only associations matching the specified category. Defaults to None.
            predicate (str, optional): Filter to only associations matching the specified predicate. Defaults to None.
            subject (str, optional): Filter to only associations matching the specified subject. Defaults to None.
            subject_closure (str, optional): Filter to only associations with the specified term ID as an ancestor of the subject. Defaults to None
            object (str, optional): Filter to only associations matching the specified object. Defaults to None.
            object_closure (str, optional): Filter to only associations with the specified term ID as an ancestor of the object. Defaults to None
            entity (str, optional): Filter to only associations where the specified entity is the subject or the object. Defaults to None.
            offset (int, optional): Result offset, for pagination. Defaults to 0.
            limit (int, optional): Limit results to specified number. Defaults to 20.

        Raises:
            NotImplementedError: Use a specific implementation (see the documentation for a list of implementations)

        Returns:
            [AssociationResults](): Dataclass representing results of an association search.
        """
        raise NotImplementedError
