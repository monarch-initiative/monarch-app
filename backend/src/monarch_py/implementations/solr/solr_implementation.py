import os
from dataclasses import dataclass
from typing import List, Union, Optional

import requests
from monarch_py.datamodels.model import (
    Association,
    AssociationCountList,
    AssociationResults,
    AssociationTableResults,
    CategoryGroupedAssociationResults,
    Entity,
    ExpandedCurie,
    HistoPheno,
    MultiEntityAssociationResults,
    Node,
    NodeHierarchy,
    SearchResults,
)
from monarch_py.datamodels.solr import core
from monarch_py.implementations.solr.solr_parsers import (
    convert_facet_fields,
    convert_facet_queries,
    parse_association_counts,
    parse_association_table,
    parse_associations,
    parse_autocomplete,
    parse_entity,
    parse_histopheno,
    parse_search,
)
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_counts_query,
    build_association_query,
    build_association_table_query,
    build_autocomplete_query,
    build_histopheno_query,
    build_multi_entity_association_query,
    build_search_query,
)
from monarch_py.interfaces.association_interface import AssociationInterface
from monarch_py.interfaces.entity_interface import EntityInterface
from monarch_py.interfaces.search_interface import SearchInterface
from monarch_py.service.curie_service import CurieService
from monarch_py.service.solr_service import SolrService
from monarch_py.utils.utils import get_provided_by_link


@dataclass
class SolrImplementation(EntityInterface, AssociationInterface, SearchInterface):
    """Implementation of Monarch Interfaces for Solr endpoint"""

    base_url: str = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")

    def solr_is_available(self) -> bool:
        """Check if the Solr instance is available"""
        try:
            return requests.get(self.base_url).status_code == 200
        except Exception:
            return False

    ###############################
    # Implements: EntityInterface #
    ###############################

    def get_entity(self, id: str, extra: bool) -> Optional[Union[Node, Entity]]:
        """Retrieve a specific entity by exact ID match, with optional extras

        Args:
            id (str): id of the entity to search for.
            extra (bool): Whether to include association counts and hierarchy in the response.

        Returns:
            Entity: Dataclass representing results of an entity search.
            Node: Dataclass representing results of an entity search with extra=True.
        """
        solr = SolrService(base_url=self.base_url, core=core.ENTITY)
        solr_document = solr.get(id)
        if solr_document is None:
            return None
        if not extra:
            return parse_entity(solr_document)

        # Get extra data (this logic is very tricky to test because of the calls to Solr)
        node = Node(**solr_document)
        if "biolink:Disease" in node.category:
            mode_of_inheritance_associations = self.get_associations(
                subject=id, predicate="biolink:has_mode_of_inheritance", offset=0
            )
            if mode_of_inheritance_associations is not None and len(mode_of_inheritance_associations.items) == 1:
                node.inheritance = self._get_associated_entity(mode_of_inheritance_associations.items[0], node)

        if "biolink:Disease" == node.category:
            node.causal_gene = [
                self._get_associated_entity(association, node)
                for association in self.get_associations(
                    object=id,
                    direct=True,
                    predicate="biolink:causes",
                    category="biolink:CausalGeneToDiseaseAssociation",
                ).items
            ]
        if "biolink:Gene" == node.category:
            node.causes_disease = [
                self._get_associated_entity(association, node)
                for association in self.get_associations(
                    subject=id,
                    direct=True,
                    predicate="biolink:causes",
                    category="biolink:CausalGeneToDiseaseAssociation",
                ).items
            ]

        node.node_hierarchy = self._get_node_hierarchy(node)
        node.association_counts = self.get_association_counts(id).items
        node.external_links = (
            [ExpandedCurie(id=curie, url=CurieService().expand(curie)) for curie in node.xref] if node.xref else []
        )
        node.provided_by_link = ExpandedCurie(
            id=node.provided_by.replace("_nodes", "").replace("_edges", "") if node.provided_by else None,
            url=get_provided_by_link(node.provided_by),
        )
        return node

    ### Entity helpers ###

    def _get_associated_entity(self, association: Association, this_entity: Entity) -> Entity:
        """Returns the id, name, and category of the other Entity in an Association given this_entity"""
        if this_entity.id == association.subject:
            entity = Entity(
                id=association.object,
                name=association.object_label,
                category=association.object_category,
            )
        elif this_entity.id == association.object:
            entity = Entity(
                id=association.subject,
                name=association.subject_label,
                category=association.subject_category,
            )
        else:
            raise ValueError(f"Association does not contain this_entity: {this_entity.id}")

        return entity

    def _get_associated_entities(
        self,
        this_entity: Entity,
        entity: str = None,
        subject: str = None,
        predicate: str = None,
        object: str = None,
    ) -> List[Entity]:
        """
        Get a list of entities directly associated with this_entity fetched from associations
        in the Solr index

        Args:
            this_entity (Entity): The entity to get associations for
            entity (str, optional): an entity ID occurring in either the subject or object. Defaults to None.
            subject (str, optional): an entity ID occurring in the subject. Defaults to None.
            predicate (str, optional): a predicate value. Defaults to None.
            object (str, optional): an entity ID occurring in the object. Defaults to None.
        """
        return [
            self._get_associated_entity(association, this_entity)
            for association in self.get_associations(
                entity=entity,
                subject=subject,
                predicate=predicate,
                object=object,
                direct=True,
                offset=0,
            ).items
        ]

    def _get_node_hierarchy(self, entity: Entity) -> NodeHierarchy:
        """
        Get a NodeHierarchy for the given entity

        Args:
            entity (Entity): The entity to get the hierarchy for
            si (SolrInterface): A SolrInterface instance

        Returns:
            NodeHierarchy: A NodeHierarchy object
        """

        super_classes = self._get_associated_entities(
            this_entity=entity, subject=entity.id, predicate="biolink:subclass_of"
        )
        sub_classes = self._get_associated_entities(
            this_entity=entity, object=entity.id, predicate="biolink:subclass_of"
        )

        return NodeHierarchy(
            super_classes=super_classes,
            sub_classes=sub_classes,
        )

    ####################################
    # Implements: AssociationInterface #
    ####################################

    def get_associations(
        self,
        category: List[str] = None,
        subject: List[str] = None,
        predicate: List[str] = None,
        object: List[str] = None,
        subject_closure: str = None,
        object_closure: str = None,
        entity: List[str] = None,
        direct: bool = None,
        offset: int = 0,
        limit: int = 20,
    ) -> AssociationResults:
        """Retrieve paginated association records, with filter options

        Args:
            category: Filter to only associations matching the specified categories. Defaults to None.
            predicate: Filter to only associations matching the specified predicates. Defaults to None.
            subject: Filter to only associations matching the specified subjects. Defaults to None.
            object: Filter to only associations matching the specified objects. Defaults to None.
            subject_closure: Filter to only associations with the specified term ID as an ancestor of the subject. Defaults to None
            object_closure: Filter to only associations with the specified term ID as an ancestor of the object. Defaults to None
            entity: Filter to only associations where the specified entities are the subject or the object. Defaults to None.
            offset: Result offset, for pagination. Defaults to 0.
            limit: Limit results to specified number. Defaults to 20.

        Returns:
            AssociationResults: Dataclass representing results of an association search.
        """

        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        query = build_association_query(
            category=[category] if isinstance(category, str) else category,
            predicate=[predicate] if isinstance(predicate, str) else predicate,
            subject=[subject] if isinstance(subject, str) else subject,
            object=[object] if isinstance(object, str) else object,
            entity=[entity] if isinstance(entity, str) else entity,
            subject_closure=subject_closure,
            object_closure=object_closure,
            direct=direct,
            offset=offset,
            limit=limit,
        )
        query_result = solr.query(query)
        associations = parse_associations(query_result)
        return associations

    def get_histopheno(self, subject_closure: str = None) -> HistoPheno:
        """Get histopheno counts for a given subject_closure"""
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        query = build_histopheno_query(subject_closure)
        query_result = solr.query(query)
        histopheno = parse_histopheno(query_result, subject_closure)
        return histopheno

    def get_multi_entity_associations(
        self,
        entity: List[str],
        counterpart_category: List[str] = None,
        offset: int = 0,
        # limit: int = 20,
        limit_per_group: int = 20,
    ) -> List[MultiEntityAssociationResults]:
        """Get associations between multiple entities and counterparts of a given category

        Args:
            entity (List[str]): List of entity IDs to get associations for
            counterpart_category (List[str], optional): List of categories of counterpart entity to get associations for. Defaults to None.
            offset (int, optional): Result offset, for pagination. Defaults to 0.
            limit (int, optional): Limit results to specified number. Defaults to 20.
            limit_per_group (int, optional): Limit results to specified number per group. Defaults to 20.
        """
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        results = []
        for entity_id in entity:
            ent = self.get_entity(entity_id, extra=False)
            if ent is None:
                results.append(
                    MultiEntityAssociationResults(
                        id=entity_id, name="Entity not found", total=0, offset=0, limit=0, associated_categories=[]
                    )
                )
                continue
            entity_result = MultiEntityAssociationResults(
                id=ent.id, name=ent.name, total=0, offset=offset, limit=limit_per_group, associated_categories=[]
            )
            if counterpart_category:
                for category in counterpart_category:
                    query = build_multi_entity_association_query(
                        entity=ent.id, counterpart_category=category, offset=offset, limit=limit_per_group
                    )
                    query_result = solr.query(query)
                    associations = parse_associations(query_result)
                    entity_result.associated_categories.append(
                        CategoryGroupedAssociationResults(
                            counterpart_category=category,
                            items=associations.items,
                            total=associations.total,
                            offset=associations.offset,
                            limit=associations.limit,
                        )
                    )
                    entity_result.total += associations.total
            results.append(entity_result)
        return results

    ###############################
    # Implements: SearchInterface #
    ###############################

    def search(
        self,
        q: str = "*:*",
        category: Union[List[str], None] = None,
        in_taxon_label: Union[List[str], None] = None,
        facet_fields: Union[List[str], None] = None,
        facet_queries: Union[List[str], None] = None,
        filter_queries: Union[List[str], None] = None,
        sort: str = None,
        offset: int = 0,
        limit: int = 20,
    ) -> SearchResults:
        """Search for entities by label, with optional filters

        Args:
            q (str): Query string. Defaults to "*:*".
            offset (int): Result offset, for pagination. Defaults to 0.
            limit (int): Limit results to specified number. Defaults to 20.
            category (List[str]): Filter to only entities matching the specified categories. Defaults to None.
            in_taxon_label (List[str]): Filter to only entities matching the specified taxon label. Defaults to None.
            facet_fields (List[str]): List of fields to include facet counts for. Defaults to None.
            facet_queries (List[str]): List of queries to include facet counts for. Defaults to None.
            filter_queries (List[str]): List of queries to filter results by. Defaults to None.
            sort (str): Sort results by the specified field. Defaults to None.

        Returns:
            SearchResults: Dataclass representing results of a search.
        """
        args = locals()
        args.pop("self", None)
        query = build_search_query(**args)
        solr = SolrService(base_url=self.base_url, core=core.ENTITY)
        query_result = solr.query(query)
        results = parse_search(query_result)
        return results

    def autocomplete(self, q: str) -> SearchResults:
        solr = SolrService(base_url=self.base_url, core=core.ENTITY)
        query = build_autocomplete_query(q)
        query_result = solr.query(query)
        results = parse_autocomplete(query_result)
        return results

    def get_association_counts(self, entity: str) -> AssociationCountList:
        """Get list of association counts for a given entity"""
        query = build_association_counts_query(entity)
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        query_result = solr.query(query)
        association_counts = parse_association_counts(query_result, entity)
        return association_counts

    def get_association_facets(
        self,
        category: List[str] = None,
        subject: List[str] = None,
        predicate: List[str] = None,
        object: List[str] = None,
        subject_closure: str = None,
        object_closure: str = None,
        entity: List[str] = None,
        facet_fields: List[str] = None,
        facet_queries: List[str] = None,
    ) -> SearchResults:
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)

        query = build_association_query(
            category=[category] if isinstance(category, str) else category,
            predicate=[predicate] if isinstance(predicate, str) else predicate,
            subject=[subject] if isinstance(subject, str) else subject,
            object=[object] if isinstance(object, str) else object,
            entity=[entity] if isinstance(entity, str) else entity,
            subject_closure=subject_closure,
            object_closure=object_closure,
            offset=0,
            limit=0,
            facet_fields=facet_fields,
            facet_queries=facet_queries,
        )
        query_result = solr.query(query)
        return SearchResults(
            limit=0,
            offset=0,
            total=query_result.response.num_found,
            items=[],
            facet_fields=convert_facet_fields(query_result.facet_counts.facet_fields)
            if query_result.facet_counts
            else [],
            facet_queries=convert_facet_queries(query_result.facet_counts.facet_queries)
            if query_result.facet_counts
            else [],
        )

    def get_association_table(
        self,
        entity: str,
        category: str,
        q: str = None,
        sort: List[str] = None,
        offset: int = 0,
        limit: int = 5,
    ) -> AssociationTableResults:
        query = build_association_table_query(
            entity=entity,
            category=category,
            q=q,
            sort=sort,
            offset=offset,
            limit=limit,
        )
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        query_result = solr.query(query)
        return parse_association_table(query_result, entity, offset, limit)
