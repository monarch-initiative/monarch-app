import pkgutil
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
        """Get the first mapping that includes the given category."""
        if AssociationTypeMappings.__instance is None:
            AssociationTypeMappings()
        for mapping in AssociationTypeMappings.__instance.mappings:
            if mapping.category and category in mapping.category:
                return mapping
        return None

    @staticmethod
    def get_mapping_by_key(key: str):
        """Get the mapping for a given section key."""
        if AssociationTypeMappings.__instance is None:
            AssociationTypeMappings()
        for mapping in AssociationTypeMappings.__instance.mappings:
            if mapping.key == key:
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

        def _first(values):
            return values[0] if values else None

        results = []
        for mapping in AssociationTypeMappings.__instance.mappings:
            category = _first(mapping.category)
            # Check if entity can be the subject
            if mapping.subject_category and entity_category in mapping.subject_category:
                results.append(
                    {
                        "category": category,
                        "label": mapping.subject_label or category,
                        "context_field": "subject",
                        "target_category": _first(mapping.object_category),
                    }
                )
            # Check if entity can be the object (reverse traversal)
            if mapping.object_category and entity_category in mapping.object_category:
                results.append(
                    {
                        "category": category,
                        "label": mapping.object_label or category,
                        "context_field": "object",
                        "target_category": _first(mapping.subject_category),
                    }
                )
        return results

    # Match criteria that are declared as (optional) lists on AssociationTypeMapping.
    # Values within a criterion are OR'd; criteria are AND'd together.
    MULTIVALUED_CRITERIA = (
        "category",
        "predicate",
        "subject_category",
        "object_category",
        "primary_knowledge_source",
        "provided_by",
    )

    def load_mappings(self):
        mapping_data = pkgutil.get_data(__package__, "./association_type_mappings.yaml")
        mapping_data = yaml.load(mapping_data, Loader=yaml.FullLoader)
        for entry in mapping_data:
            # allow scalar shorthand in the yaml for the multivalued criteria
            for field in AssociationTypeMappings.MULTIVALUED_CRITERIA:
                value = entry.get(field)
                if value is not None and not isinstance(value, list):
                    entry[field] = [value]
            # default the section key to the (single) category when not set
            if not entry.get("key"):
                category = entry.get("category")
                if category:
                    entry["key"] = category[0]
        adapter = TypeAdapter(List[AssociationTypeMapping])
        self.mappings = adapter.validate_python(mapping_data)


def _or_group(field: str, values) -> str:
    """Build a Solr clause for one match criterion: OR within the field.

    A single value renders without parentheses so single-category mappings
    produce exactly the same query as before (e.g. `category:"biolink:X"`).
    """
    if not values:
        return None
    if isinstance(values, str):
        values = [values]
    if len(values) == 1:
        return f'{field}:"{values[0]}"'
    return "(" + " OR ".join(f'{field}:"{value}"' for value in values) + ")"


def get_solr_query_fragment(agm: AssociationTypeMapping) -> str:
    """Build the Solr clause that selects this association type: AND across the
    present criteria, each criterion OR'd internally."""
    parts = [
        _or_group("category", agm.category),
        _or_group("predicate", agm.predicate),
        _or_group("subject_category", agm.subject_category),
        _or_group("object_category", agm.object_category),
        _or_group("primary_knowledge_source", agm.primary_knowledge_source),
        _or_group("provided_by", agm.provided_by),
    ]
    return " AND ".join(part for part in parts if part)


def get_solr_criteria_filters(agm: AssociationTypeMapping) -> List[str]:
    """The non-category match criteria as individual Solr filter-query clauses.

    Used by the association table query, where the category list is applied
    separately and predicate / subject / object / source criteria are added as
    additional filters.
    """
    return [
        clause
        for clause in (
            _or_group("predicate", agm.predicate),
            _or_group("subject_category", agm.subject_category),
            _or_group("object_category", agm.object_category),
            _or_group("primary_knowledge_source", agm.primary_knowledge_source),
            _or_group("provided_by", agm.provided_by),
        )
        if clause
    ]


def get_sql_query_fragment(agm: AssociationTypeMapping) -> str:
    """SQL equivalent of get_solr_query_fragment (AND across criteria, OR within)."""

    def _or_group_sql(field, values):
        if not values:
            return None
        if isinstance(values, str):
            values = [values]
        if len(values) == 1:
            return f'{field} = "{values[0]}"'
        return "(" + " OR ".join(f'{field} = "{value}"' for value in values) + ")"

    parts = [
        _or_group_sql("category", agm.category),
        _or_group_sql("predicate", agm.predicate),
        _or_group_sql("subject_category", agm.subject_category),
        _or_group_sql("object_category", agm.object_category),
        _or_group_sql("primary_knowledge_source", agm.primary_knowledge_source),
        _or_group_sql("provided_by", agm.provided_by),
    ]
    return " AND ".join(part for part in parts if part)
