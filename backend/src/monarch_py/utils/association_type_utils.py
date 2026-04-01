import pkgutil
import re
from typing import List

import yaml
from monarch_py.datamodels.model import AssociationTypeMapping
from pydantic import TypeAdapter


class AssociationTypeMappings:
    __instance = None

    def __init__(self):
        if AssociationTypeMappings.__instance is not None:
            raise Exception("AssociationTypeMappings is a singleton class, use getInstance() to get the instance.")
        else:
            AssociationTypeMappings.__instance = self
            self.mappings = None
            self.load_mappings()

    @staticmethod
    def get_mappings():
        if AssociationTypeMappings.__instance is None:
            AssociationTypeMappings()
        return AssociationTypeMappings.__instance.mappings

    @staticmethod
    def get_mapping(category: str):
        if AssociationTypeMappings.__instance is None:
            AssociationTypeMappings()
        for mapping in AssociationTypeMappings.__instance.mappings:
            if mapping.category == category:
                return mapping
        return None

    @staticmethod
    def get_traversable_associations(entity_category: str) -> List[dict]:
        """Get associations traversable from a given entity category.

        Returns associations where the entity can be either subject or object,
        with direction info indicating which field the entity occupies.

        Args:
            entity_category: The biolink category of the context entity (e.g., "biolink:Gene")

        Returns:
            List of dicts with:
            - category: association category string
            - label: display label for UI
            - context_field: "subject" or "object" (where context entity appears)
            - target_category: what entity type the other end is
        """
        if AssociationTypeMappings.__instance is None:
            AssociationTypeMappings()

        results = []
        for mapping in AssociationTypeMappings.__instance.mappings:
            # Check if entity can be the subject
            if mapping.subject_category == entity_category:
                results.append(
                    {
                        "category": mapping.category,
                        "label": mapping.subject_label or mapping.category,
                        "context_field": "subject",
                        "target_category": mapping.object_category,
                    }
                )
            # Check if entity can be the object (reverse traversal)
            if mapping.object_category == entity_category:
                results.append(
                    {
                        "category": mapping.category,
                        "label": mapping.object_label or mapping.category,
                        "context_field": "object",
                        "target_category": mapping.subject_category,
                    }
                )
        return results

    def load_mappings(self):
        mapping_data = pkgutil.get_data(__package__, "./association_type_mappings.yaml")
        mapping_data = yaml.load(mapping_data, Loader=yaml.FullLoader)
        adapter = TypeAdapter(List[AssociationTypeMapping])
        self.mappings = adapter.validate_python(mapping_data)


def get_association_type_mapping_by_query_string(
    query_string: str,
) -> AssociationTypeMapping:
    """
    Get the association type mapping for a given query string, splitting the category and predicate components apart
    Args:
        query_string: A solr query string to parse apart for category and predicate

    Returns: An AssociationTypeMapping instance appropriate for the given query string
    Raises: ValueError if no match is found
    """

    category = parse_query_string_for_category(query_string)

    matching_types = [a_type for a_type in AssociationTypeMappings.get_mappings() if a_type.category == category]

    if len(matching_types) == 0:
        raise ValueError(f"No matching association type found for query string: [{query_string}]")
    elif len(matching_types) > 1:
        raise ValueError(f"Too many association types found for query string: [{query_string}]")
    else:
        return matching_types[0]


def get_solr_query_fragment(agm: AssociationTypeMapping) -> str:
    return f'category:"{agm.category}"'


def get_sql_query_fragment(agm: AssociationTypeMapping) -> str:
    return f'category = "{agm.category}"'


def parse_query_string_for_category(
    query_string: str,
) -> str:
    categories = []

    pattern = re.compile(r'(category):\s*"?([\w:]+)"?')
    for match in re.findall(pattern, query_string):
        if match[0] == "category":
            categories.append(match[1])

    # Check if both categories and predicates were found
    if not categories:
        raise ValueError("No categories or predicates found in query string")

    if len(categories) > 1:
        raise ValueError(f"Multiple categories found in query string: {query_string}")

    return categories[0]
