from monarch_api.model import Association, Entity, NodeHierarchy
from monarch_py.implementations.solr.solr_implementation import SolrImplementation


def get_associated_entity(association: Association, this_entity: Entity) -> Entity:
    """
    Convert an Association to an Entity by extracting the subject or object
    (whichever is not this_entity) and setting the id, name and category on
    the returned Entity

    Args:
        association (Association): A single association, expected to contain `this_entity`
        this_entity (Entity): The Entity that you don't want returned

    Returns:
        Entity: A limited representation of the entity associated with `this_entity`
    """
    if association.subject == this_entity.id:
        entity = Entity(id = association.object,
                        name = association.object_label,
                        category = association.object_category)
    elif association.object == this_entity.id:
        entity = Entity(id = association.subject,
                        name = association.subject_label,
                        category = association.subject_category)
    else:
        raise ValueError(f"Association does not contain this_entity: {this_entity.id}")

    return entity

def get_hierarchy(entity: Entity, si: SolrImplementation) -> NodeHierarchy:
    """
    Get a NodeHierarchy for the given entity

    Args:
        entity (Entity): The entity to get the hierarchy for
        si (SolrInterface): A SolrInterface instance

    Returns:
        NodeHierarchy: A NodeHierarchy object
    """
    # todo: review predicates, plan for empty results
    return NodeHierarchy(
        super_classes=si.get_associations(subject=entity.id, predicate="biolink:subclass_of").associations,
        equivalent_classes=si.get_associations(entity=entity.id, predicate="biolink:same_as").associations,
        sub_classes=si.get_associations(object=entity.id, predicate="biolink:subclass_of").associations,
    )

