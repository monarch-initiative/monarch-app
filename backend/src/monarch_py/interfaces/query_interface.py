from abc import ABC, abstractmethod

from monarch_py.datamodels.model import EntityResults


class QueryInterface(ABC):
    """Abstract interface for querying the Monarch KG in a SQL way"""

    @abstractmethod
    def query(self) -> EntityResults:
        """

        Args:
            q (str): Query string to match against
            category (str): Limit results to only this category
            taxon (str): Limit results to only this taxon
            offset (int): Offset of the first result to return, defaults to 0
            limit (int): Limit the number of results to return, defaults to 20

        Raises:
            NotImplementedError: Use a specific implementation (see the documentation for a list of implementations)

        Returns:
            EntityResults: Dataclass representing results of a generic entity search.
        """
        raise NotImplementedError
