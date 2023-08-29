from dataclasses import dataclass
from typing import List

import pystow
from loguru import logger
from monarch_py.datamodels.model import Association, AssociationResults, Entity, Node, NodeHierarchy
from monarch_py.interfaces.association_interface import AssociationInterface
from monarch_py.interfaces.entity_interface import EntityInterface
from monarch_py.utils.utils import SQL_DATA_URL, dict_factory
from pydantic import ValidationError

monarchstow = pystow.module("monarch")


@dataclass
class SQLImplementation(EntityInterface, AssociationInterface):
    """Implementation of Monarch Interfaces for SQL endpoint"""

    ###############################
    # Implements: EntityInterface #
    ###############################

    def get_entity(self, id: str, update: bool = False, extra: bool = False) -> Entity:
        """Retrieve a specific entity by exact ID match, writh optional extras

        Args:
            id (str): id of the entity to search for.
            get_association_counts (bool, optional): Whether to get association counts. Defaults to False.
            get_hierarchy (bool, optional): Whether to get the entity hierarchy. Defaults to False.

        Returns:
            Entity: Dataclass representing results of an entity search.
        """

        with monarchstow.ensure_open_sqlite_gz("sql", url=SQL_DATA_URL, force=update) as db:
            db.row_factory = dict_factory
            cur = db.cursor()
            sql_data = cur.execute(f"SELECT * FROM nodes WHERE id = '{id}'").fetchone()

        if not sql_data:
            return None
        results = {
            "id": sql_data["id"],
            "category": sql_data["category"],  # .split("|"), # This will become a list in the future
            "name": sql_data["name"],
            "description": sql_data["description"],
            "xref": sql_data["xref"].split("|"),
            "provided_by": sql_data["provided_by"],
            "in_taxon": sql_data["in_taxon"],
            "symbol": sql_data["symbol"],
            "synonym": sql_data["synonym"].split("|"),
        }
        try:
            results["source"] = sql_data["source"]
        except KeyError:
            pass
        # Convert empty strings to null value
        for k in results:
            results[k] = None if not results[k] else results[k]

        if not extra:
            try:
                return Entity(**results)
            except ValidationError:
                logger.error(f"Validation error for {sql_data}")
                raise

        node = Node(**results)

        if "biolink:Disease" in node.category:
            mode_of_inheritance_associations = self.get_associations(
                subject=id, predicate="biolink:has_mode_of_inheritance", offset=0
            )
        if mode_of_inheritance_associations is not None and len(mode_of_inheritance_associations.items) == 1:
            node.inheritance = self._get_associated_entity(mode_of_inheritance_associations.items[0], node)
        node.node_hierarchy = self._get_node_hierarchy(node)
        ### SQL does not support association counts
        return node

    def _get_associated_entity(self, association: Association, this_entity: Entity) -> Entity:
        """Returns the other Entity in an Association given this_entity"""
        if this_entity.id in association.subject_closure:
            entity = Entity(
                id=association.object,
                name=association.object_label,
                category=association.object_category if len(association.object_category) == 1 else [],
            )
        elif this_entity.id in association.object_closure:
            entity = Entity(
                id=association.subject,
                name=association.subject_label,
                category=association.subject_category if len(association.subject_category) == 1 else [],
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
            entity (str, optional): an entity ID occurring in either the subject or predicate. Defaults to None.
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
            category (str, optional): Filter to only associations matching the specified category. Defaults to None.
            predicate (str, optional): Filter to only associations matching the specified predicate. Defaults to None.
            subject (str, optional): Filter to only associations matching the specified subject. Defaults to None.
            object (str, optional): Filter to only associations matching the specified object. Defaults to None.
            subject_closure (str, optional): Filter to only associations with the specified term ID as an ancestor of the subject. Defaults to None.
            object_closure (str, optional): Filter to only associations the specified term ID as an ancestor of the object. Defaults to None.
            entity (str, optional): Filter to only associations where the specified entity is the subject or the object. Defaults to None.
            association_type (str, optional): Filter to only associations matching the specified association label. Defaults to None.
            offset (int, optional): Result offset, for pagination. Defaults to 0.
            limit (int, optional): Limit results to specified number. Defaults to 20.

        Returns:
            AssociationResults: Dataclass representing results of an association search.
        """

        clauses = []
        if category:
            clauses.append(" OR ".join([f"category = '{c}'" for c in category]))
        if subject:
            if direct:
                clauses.append(" OR ".join([f"subject = '{s}'" for s in subject]))
            else:
                clauses.append(" OR ".join([f"subject = '{s}' OR subject_closure like '%{s}%'" for s in subject]))
        if predicate:
            clauses.append(" OR ".join([f"predicate = '{p}'" for p in predicate]))
        if object:
            if direct:
                clauses.append(" OR ".join([f"object = '{o}'" for o in object]))
            else:
                clauses.append(" OR ".join([f"object = '{o}' OR object_closure like '%{o}%'" for o in object]))
        if subject_closure:
            clauses.append(f"subject_closure like '%{subject_closure}%'")
        if object_closure:
            clauses.append(f"object_closure like '%{object_closure}%'")
        if entity:
            if direct:
                clauses.append(" OR ".join([f"subject = '{e}' OR object = '{e}'" for e in entity]))
            else:
                clauses.append(
                    " OR ".join(
                        [
                            f"subject = '{e}' OR object = '{e}' OR subject_closure like '%{e}%' OR object_closure like '%{e}%'"
                            for e in entity
                        ]
                    )
                )

        query = f"SELECT * FROM denormalized_edges "
        if clauses:
            query += "WHERE " + " AND ".join(clauses)
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        count_query = f"SELECT COUNT(*) FROM denormalized_edges "
        if clauses:
            count_query += "WHERE " + " AND ".join(clauses)

        with monarchstow.ensure_open_sqlite_gz("sql", url=SQL_DATA_URL) as db:
            db.row_factory = dict_factory
            cur = db.cursor()
            results = cur.execute(query).fetchall()
            count = cur.execute(count_query).fetchone()
            total = count[f"COUNT(*)"]

        associations = []
        for row in results:
            result = {
                "id": row["id"],
                "original_subject": row["original_subject"],
                "predicate": row["predicate"],
                "original_object": row["original_object"],
                "category": row["category"],
                "aggregator_knowledge_source": row["aggregator_knowledge_source"].split("|"),
                "primary_knowledge_source": row["primary_knowledge_source"],
                "publications": row["publications"].split("|"),
                "qualifiers": row["qualifiers"].split("|"),
                "provided_by": row["provided_by"],
                "has_evidence": row["has_evidence"].split("|"),
                "stage_qualifier": row["stage_qualifier"],
                "negated": False if not row["negated"] else True,
                "frequency_qualifier": row["frequency_qualifier"],
                "onset_qualifier": row["onset_qualifier"],
                "sex_qualifier": row["sex_qualifier"],
                "subject": row["subject"],
                "object": row["object"],
            }
            # Convert empty strings to null value
            for key in result:
                result[key] = None if not result[key] else result[key]
            try:
                associations.append(Association(**result))
            except ValidationError:
                logger.error(f"Validation error for {row}")
                raise

        results = AssociationResults(items=associations, limit=limit, offset=offset, total=total)
        return results
