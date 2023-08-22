import pkgutil
import re
from typing import List

import yaml
from monarch_py.datamodels.model import AssociationTypeMapping
from pydantic import parse_obj_as


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

    def get_mapping(self, category: str):
        if AssociationTypeMappings.__instance is None:
            AssociationTypeMappings()
        for mapping in self.mappings:
            if mapping.category == category:
                return mapping

    def load_mappings(self):
        mapping_data = pkgutil.get_data(__package__, "./association_type_mappings.yaml")
        mapping_data = yaml.load(mapping_data, Loader=yaml.FullLoader)
        self.mappings = parse_obj_as(List[AssociationTypeMapping], mapping_data)


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

    categories = parse_query_string_for_category(query_string)

    matching_types = [
        a_type for a_type in AssociationTypeMappings.get_mappings() if set(a_type.category) == set(categories)
    ]

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
