from abc import ABC, abstractmethod
from typing import List

from monarch_py.datamodels.model import AssociationTableResults, FacetValue, SearchResults


class SearchInterface(ABC):
    """Abstract interface for searching the Monarch KG in a Lucene way"""

    @abstractmethod
    def search(
        self,
        q: str,
        offset: int = 0,
        limit: int = 20,
        category: List[str] = None,
        in_taxon: List[str] = None,
        facet_fields: List[str] = None,
        filter_queries: List[str] = None,
        facet_queries: List[str] = None,
        sort: str = None,
    ) -> SearchResults:
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

    def autocomplete(self, q: str) -> SearchResults:
        """

        Args:
            q (str): Query string to match against

        Raises:
            NotImplementedError: Use a specific implementation (see the documentation for a list of implementations)

        Returns:
            SearchResults: Dataclass representing results of a generic entity search.
        """
        raise NotImplementedError

    def get_association_facets(
        self,
        facet_fields: List[str] = None,
        facet_queries: List[str] = None,
        category: str = None,
        predicate: str = None,
        subject: str = None,
        subject_closure: str = None,
        object: str = None,
        object_closure: str = None,
        entity: str = None,
    ) -> SearchResults:
        """
        Get facet counts and facet query counts for associations
        Args:
            facet_fields (List[str]): Facet fields to return counts for
            facet_queries (List[str]): Facet queries to return counts for
            category (str): Filter to only associations matching the specified category
            predicate (str): Filter to only associations matching the specified predicate
            subject (str): Filter to only associations matching the specified subject
            subject_closure (str): Filter to only associations with the specified term ID as an ancestor of the subject
            object (str): Filter to only associations matching the specified object
            object_closure (str): Filter to only associations with the specified term ID as an ancestor of the object
            entity (str): Filter to only associations where the specified entity is the subject or the object
        Returns:
            SearchResults: Dataclass representing results of a search, with zero rows returned but total count
            and faceting information populated
        """
        raise NotImplementedError

    def get_association_counts(self, entity: str) -> List[FacetValue]:
        """
        Get counts of associations for a given entity
        Args:
            entity (str): Entity to get association counts for
        Returns:
            List[FacetValue]: List of FacetValue objects representing the counts of associations for the given entity
        """
        raise NotImplementedError

    def get_association_table(
        self,
        entity: str,
        category: str,
        query=None,
        sort=None,
        offset=0,
        limit=5,
    ) -> AssociationTableResults:
        """
        Get associations for an entity matching a specified type, with optional search and sort parameters

        Args:
            entity (str): Entity to get associations for
            category (str): Category of associations to return
            query (str): Query string to match against
            sort (str): Sort order, defaults to None
            offset (int): Offset of the first result to return, defaults to 0
            limit (int): Limit the number of results to return, defaults to 20

        Returns:
            AssociationResults: Dataclass representing results of an association search.
        """

        raise NotImplementedError
