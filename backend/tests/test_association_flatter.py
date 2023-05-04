import pytest
from monarch_api.model import Association, Entity
from monarch_api.utils.entity_utils import get_associated_entity


@pytest.fixture()
def example_association():
    return Association(
        subject="MONDO:0007947",
        subject_label="Marfan syndrome",
        subject_category=["biolink:Disease"],
        subject_closure=["MONDO:0007947", "MONDO:0000001"],
        predicate="biolink:has_mode_of_inheritance",
        object="HP:0000006",
        object_label="Autosomal dominant inheritance",
        object_category=["biolink:ModeOfInheritance"],
        object_closure=["HP:0000006", "HP:0000005"],
    )


def test_get_associated_entity_from_object(example_association):

    this_entity = Entity(id="MONDO:0007947")

    associated_entity = get_associated_entity(example_association, this_entity)

    assert associated_entity.id == "HP:0000006"
    assert associated_entity.name == "Autosomal dominant inheritance"
    assert associated_entity.category == ["biolink:ModeOfInheritance"]


def test_get_associated_entity_from_subject(example_association):

    this_entity = Entity(id="HP:0000006")

    associated_entity = get_associated_entity(example_association, this_entity)

    assert associated_entity.id == "MONDO:0007947"
    assert associated_entity.name == "Marfan syndrome"
    assert associated_entity.category == ["biolink:Disease"]
