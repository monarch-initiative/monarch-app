import os
from dataclasses import dataclass
from typing import List, Union, Optional

import requests
from monarch_py.datamodels.model import (
    Association,
    CompactAssociation,
    AssociationCountList,
    AssociationResults,
    AssociationTableResults,
    CategoryGroupedAssociationResults,
    Entity,
    HistoPheno,
    MappingResults,
    MultiEntityAssociationResults,
    Node,
    NodeHierarchy,
    SearchResults,
)
from monarch_py.datamodels.solr import core
from monarch_py.datamodels.category_enums import (
    AssociationCategory,
    AssociationPredicate,
    EntityCategory,
    MappingPredicate,
)
from monarch_py.implementations.solr.solr_parsers import (
    convert_facet_fields,
    convert_facet_queries,
    parse_association_counts,
    parse_association_table,
    parse_associations,
    parse_autocomplete,
    parse_entity,
    parse_histopheno,
    parse_mappings,
    parse_search,
)
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_counts_query,
    build_association_query,
    build_association_table_query,
    build_autocomplete_query,
    build_histopheno_query,
    build_mapping_query,
    build_multi_entity_association_query,
    build_search_query,
    build_grounding_query,
)
from monarch_py.interfaces.association_interface import AssociationInterface
from monarch_py.interfaces.entity_interface import EntityInterface
from monarch_py.interfaces.search_interface import SearchInterface
from monarch_py.interfaces.grounding_interface import GroundingInterface
from monarch_py.service.solr_service import SolrService
from monarch_py.utils.entity_utils import get_expanded_curie, get_uri
from monarch_py.utils.utils import get_provided_by_link, get_links_for_field


@dataclass
class SolrImplementation(EntityInterface, AssociationInterface, SearchInterface, GroundingInterface):
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
        entity = Entity(**solr_document)
        entity.uri = get_uri(entity.id)
        if "biolink:Disease" == entity.category:
            # Get mode of inheritance
            mode_of_inheritance_associations = self.get_associations(
                subject=id, predicate=[AssociationPredicate.HAS_MODE_OF_INHERITANCE], direct=True, offset=0
            )
            if mode_of_inheritance_associations is not None and len(mode_of_inheritance_associations.items) == 1:
                entity.inheritance = self._get_counterpart_entity(mode_of_inheritance_associations.items[0], entity)
            # Get causal gene
            entity.causal_gene = [
                self._get_counterpart_entity(association, entity)
                for association in self.get_associations(
                    object=id,
                    direct=True,
                    predicate=[AssociationPredicate.CAUSES],
                    category=[AssociationCategory.CAUSAL_GENE_TO_DISEASE_ASSOCIATION],
                ).items
            ]
        if "biolink:Gene" == entity.category:
            entity.causes_disease = [
                self._get_counterpart_entity(association, entity)
                for association in self.get_associations(
                    subject=id,
                    direct=True,
                    predicate=[AssociationPredicate.CAUSES],
                    category=[AssociationCategory.CAUSAL_GENE_TO_DISEASE_ASSOCIATION],
                ).items
            ]
        node: Node = Node(
            **entity.model_dump(),
            node_hierarchy=self._get_node_hierarchy(entity),
            association_counts=self.get_association_counts(id).items,
            external_links=get_links_for_field(entity.xref) if entity.xref else [],
            provided_by_link=get_provided_by_link(entity.provided_by),
            mappings=self._get_mapped_entities(entity),
        )

        return node

    ### Entity helpers ###

    def _get_mapped_entities(self, this_entity: Entity) -> list:
        """..."""
        mapped_entities = []
        mappings = self.get_mappings(entity_id=this_entity.id)
        for m in mappings.items:
            if this_entity.id == m.subject_id:
                mapped_entities.append(get_expanded_curie(m.object_id))
            elif this_entity.id == m.object_id:
                mapped_entities.append(get_expanded_curie(m.subject_id))
            else:
                pass
        return mapped_entities

    def _get_counterpart_entity(self, association: Association, this_entity: Entity) -> Entity:
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

    def get_counterpart_entities(
        self,
        this_entity: Entity,
        entity: Optional[str] = None,
        subject: Optional[str] = None,
        predicate: List[AssociationPredicate] = None,
        object: Optional[str] = None,
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
            self._get_counterpart_entity(association, this_entity)
            for association in self.get_associations(
                entity=entity,
                subject=subject,
                predicate=predicate,
                object=object,
                direct=True,
                limit=1000,
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

        super_classes = self.get_counterpart_entities(
            this_entity=entity, subject=entity.id, predicate=[AssociationPredicate.SUBCLASS_OF]
        )
        sub_classes = self.get_counterpart_entities(
            this_entity=entity, object=entity.id, predicate=[AssociationPredicate.SUBCLASS_OF]
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
        category: List[AssociationCategory] = None,
        subject: Optional[List[str]] = None,
        subject_closure: Optional[str] = None,
        subject_category: List[EntityCategory] = None,
        subject_namespace: Optional[List[str]] = None,
        subject_taxon: Optional[List[str]] = None,
        predicate: List[AssociationPredicate] = None,
        object: Optional[List[str]] = None,
        object_closure: Optional[str] = None,
        object_category: List[EntityCategory] = None,
        object_namespace: Optional[List[str]] = None,
        object_taxon: Optional[List[str]] = None,
        entity: Optional[List[str]] = None,
        direct: bool = False,
        q: Optional[str] = None,
        facet_fields: Optional[List[str]] = None,
        facet_queries: Optional[List[str]] = None,
        filter_queries: Optional[List[str]] = None,
        compact: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> Union[AssociationResults, CompactAssociation]:
        """Retrieve paginated association records, with filter options

        Args:
            category: Filter to only associations matching the specified categories. Defaults to None.
            predicate: Filter to only associations matching the specified predicates. Defaults to None.
            subject: Filter to only associations matching the specified subjects. Defaults to None.
            object: Filter to only associations matching the specified objects. Defaults to None.
            subject_closure: Filter to only associations with the specified term ID as an ancestor of the subject. Defaults to None
            object_closure: Filter to only associations with the specified term ID as an ancestor of the object. Defaults to None
            entity: Filter to only associations where the specified entities are the subject or the object. Defaults to None.
            q: Query string to search within matches. Defaults to None.
            facet_fields: List of fields to include facet counts for. Defaults to None.
            facet_queries: List of queries to include facet counts for. Defaults to None.
            filter_queries: List of queries to filter results by. Defaults to None.
            compact: Return compact results with fewer fields. Defaults to False.
            offset: Result offset, for pagination. Defaults to 0.
            limit: Limit results to specified number. Defaults to 20.

        Returns:
            AssociationResults: Dataclass representing results of an association search.
        """
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        query = build_association_query(
            category=[c.value for c in category] if category else [],
            predicate=[p.value for p in predicate] if predicate else [],
            subject=[subject] if isinstance(subject, str) else subject,
            object=[object] if isinstance(object, str) else object,
            entity=[entity] if isinstance(entity, str) else entity,
            subject_closure=subject_closure,
            object_closure=object_closure,
            subject_category=[c.value for c in subject_category] if subject_category else [],
            subject_namespace=[subject_namespace] if isinstance(subject_namespace, str) else subject_namespace,
            subject_taxon=[subject_taxon] if isinstance(subject_taxon, str) else subject_taxon,
            object_category=[c.value for c in object_category] if object_category else [],
            object_taxon=[object_taxon] if isinstance(object_taxon, str) else object_taxon,
            object_namespace=[object_namespace] if isinstance(object_namespace, str) else object_namespace,
            direct=direct,
            q=q,
            facet_fields=facet_fields,
            facet_queries=facet_queries,
            filter_queries=filter_queries,
            offset=offset,
            limit=limit,
        )
        query_result = solr.query(query)

        associations = parse_associations(query_result, compact, offset, limit)
        return associations

    def get_histopheno(self, subject: Optional[str] = None) -> HistoPheno:
        """Get histopheno counts for a given subject_closure"""
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        query = build_histopheno_query(subject)
        query_result = solr.query(query)
        histopheno = parse_histopheno(query_result, subject)
        return histopheno

    def get_multi_entity_associations(
        self,
        entity: List[str],
        counterpart_category: Optional[List[str]] = None,
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
        category: Union[List[EntityCategory], None] = None,
        in_taxon_label: Union[List[str], None] = None,
        facet_fields: Union[List[str], None] = None,
        facet_queries: Union[List[str], None] = None,
        filter_queries: Union[List[str], None] = None,
        sort: Optional[str] = None,
        highlighting: bool = False,
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
        query = build_search_query(
            q=q,
            category=[c.value for c in category] if category else None,
            in_taxon_label=in_taxon_label,
            facet_fields=facet_fields,
            facet_queries=facet_queries,
            filter_queries=filter_queries,
            highlighting=highlighting,
            sort=sort,
            offset=offset,
            limit=limit,
        )
        solr = SolrService(base_url=self.base_url, core=core.ENTITY)
        query_result = solr.query(query)
        results = parse_search(query_result)
        return results

    def autocomplete(
        self, q: str, category: List[EntityCategory] = None, prioritized_predicates: List[AssociationPredicate] = None
    ) -> SearchResults:
        solr = SolrService(base_url=self.base_url, core=core.ENTITY)
        query = build_autocomplete_query(
            q,
            category=[cat.value for cat in category] if category else None,
            prioritized_predicates=prioritized_predicates,
        )
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
        category: List[AssociationCategory] = None,
        subject: Optional[List[str]] = None,
        predicate: List[AssociationPredicate] = None,
        object: Optional[List[str]] = None,
        subject_closure: Optional[str] = None,
        object_closure: Optional[str] = None,
        entity: Optional[List[str]] = None,
        facet_fields: Optional[List[str]] = None,
        facet_queries: Optional[List[str]] = None,
        filter_queries: Optional[List[str]] = None,
    ) -> SearchResults:
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)

        query = build_association_query(
            category=[c.value for c in category] if category else None,
            predicate=[p.value for p in predicate] if predicate else None,
            subject=[subject] if isinstance(subject, str) else subject,
            object=[object] if isinstance(object, str) else object,
            entity=[entity] if isinstance(entity, str) else entity,
            subject_closure=subject_closure,
            object_closure=object_closure,
            offset=0,
            limit=0,
            facet_fields=facet_fields,
            facet_queries=facet_queries,
            filter_queries=filter_queries,
        )
        query_result = solr.query(query)
        return SearchResults(
            limit=0,
            offset=0,
            total=query_result.response.num_found,
            items=[],
            facet_fields=(
                convert_facet_fields(query_result.facet_counts.facet_fields) if query_result.facet_counts else []
            ),
            facet_queries=(
                convert_facet_queries(query_result.facet_counts.facet_queries) if query_result.facet_counts else []
            ),
        )

    def get_association_table(
        self,
        entity: str,
        category: AssociationCategory,
        traverse_orthologs: bool = False,
        direct: bool = False,
        q: Optional[str] = None,
        facet_fields: Optional[List[str]] = None,
        facet_queries: Optional[List[str]] = None,
        filter_queries: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 5,
    ) -> AssociationTableResults:
        entities = [entity]
        if traverse_orthologs:
            ortholog_associations = self.get_associations(
                entity=[entity], predicate=[AssociationPredicate.ORTHOLOGOUS_TO]
            )
            orthologous_entities = [
                self._get_counterpart_entity(a, Entity(id=entity)) for a in ortholog_associations.items
            ]
            entities.extend([ent.id for ent in orthologous_entities])
        query = build_association_table_query(
            entity=entities,
            category=category.value,
            direct=direct,
            q=q,
            facet_fields=facet_fields,
            facet_queries=facet_queries,
            filter_queries=filter_queries,
            sort=sort,
            offset=offset,
            limit=limit,
        )
        solr = SolrService(base_url=self.base_url, core=core.ASSOCIATION)
        query_result = solr.query(query)
        return parse_association_table(query_result, entities, offset, limit)

    def get_mappings(
        self,
        entity_id: Optional[List[str]] = None,
        subject_id: Optional[List[str]] = None,
        predicate_id: Optional[List[MappingPredicate]] = None,
        object_id: Optional[List[str]] = None,
        mapping_justification: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> MappingResults:
        solr = SolrService(base_url=self.base_url, core=core.SSSOM)
        query = build_mapping_query(
            entity_id=[entity_id] if isinstance(entity_id, str) else entity_id,
            subject_id=[subject_id] if isinstance(subject_id, str) else subject_id,
            predicate_id=[p.value for p in predicate_id] if predicate_id else None,
            object_id=[object_id] if isinstance(object_id, str) else object_id,
            mapping_justification=(
                [mapping_justification] if isinstance(mapping_justification, str) else mapping_justification
            ),
            offset=offset,
            limit=limit,
        )
        query_result = solr.query(query)
        mappings = parse_mappings(query_result, offset, limit)
        return mappings

    ##################################
    # Implements: GroundingInterface #
    ##################################

    def ground_entity(self, text: str) -> List[Entity]:
        """Grounds a single entity

        Args:
            text (str): Text to ground

        Returns:
            Entity: Dataclass representing a single entity
        """
        solr = SolrService(base_url=self.base_url, core=core.ENTITY)
        query = build_grounding_query(text)
        query_result = solr.query(query)
        search_result = parse_search(query_result)
        entities = [entity for entity in search_result.items[:3]]
        return entities
