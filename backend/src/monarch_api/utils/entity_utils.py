from typing import List

from monarch_api.model import Association, Entity, NodeHierarchy
from monarch_py.implementations.solr.solr_implementation import SolrImplementation


def get_associated_entity(association: Association, this_entity: Entity) -> Entity:
    """
    Convert an Association to an Entity by extracting the subject or object
    (whichever is not this_entity) and setting the id, name and category on
    the returned Entity.

    If ever we need to add more fields, we'll need to add additional expansions
    in the closurizer repo that produces the denormalized kgx file that we use
    to populate the solr index.

    Args:
        association (Association): A single association, expected to contain `this_entity`
        this_entity (Entity): The Entity that you don't want returned

    Returns:
        Entity: A limited representation of the entity associated with `this_entity`
    """
    # if association.subject == this_entity.id:
    if this_entity.id in association.subject_closure:
        entity = Entity(
            id=association.object,
            name=association.object_label,
            # this will be replaced when category is single valued on associations
            category=association.object_category,
        )
    # elif association.object == this_entity.id:
    elif this_entity.id in association.object_closure:
        entity = Entity(
            id=association.subject,
            name=association.subject_label,
            # this will be replaced when category is single valued on associations
            category=association.subject_category,
        )
    else:
        raise ValueError(f"Association does not contain this_entity: {this_entity.id}")

    return entity


def get_associated_entities(
    this_entity: Entity,
    si: SolrImplementation,
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
        si (SolrInterface): A SolrInterface instance
        entity (str, optional): an entity ID occurring in either the subject or predicate. Defaults to None.
        subject (str, optional): an entity ID occurring in the subject. Defaults to None.
        predicate (str, optional): a predicate value. Defaults to None.
        object (str, optional): an entity ID occurring in the object. Defaults to None.
    """
    return [
        get_associated_entity(association, this_entity)
        for association in si.get_associations(
            entity=entity,
            subject=subject,
            predicate=predicate,
            object=object,
            direct=True,
            offset=0,
        ).items
    ]


def get_node_hierarchy(entity: Entity, si: SolrImplementation) -> NodeHierarchy:
    """
    Get a NodeHierarchy for the given entity

    Args:
        entity (Entity): The entity to get the hierarchy for
        si (SolrInterface): A SolrInterface instance

    Returns:
        NodeHierarchy: A NodeHierarchy object
    """

    super_classes = get_associated_entities(
        entity, si, subject=entity.id, predicate="biolink:subclass_of"
    )
    equivalent_classes = get_associated_entities(
        entity, si, entity=entity.id, predicate="biolink:same_as"
    )
    sub_classes = get_associated_entities(
        entity, si, object=entity.id, predicate="biolink:subclass_of"
    )

    return NodeHierarchy(
        super_classes=super_classes,
        equivalent_classes=equivalent_classes,
        sub_classes=sub_classes,
    )
