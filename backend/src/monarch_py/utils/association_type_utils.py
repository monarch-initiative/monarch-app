import pkgutil
from typing import List

import yaml
from monarch_py.datamodels.model import AssociationTypeMapping, MatchCriteriaEnum
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
            - key: the section key, which identifies the section unambiguously
            - category: the section's first association category, for callers that still
              key on a single category. Prefer `key`: several sections can share a category
              (every LOINC section is biolink:Association), so this does not identify one.
            - categories: every category the section matches
            - label: display label for UI
            - context_field: "subject" or "object" (where context entity appears)
            - target_category: what entity type the other end is
            - target_categories: every category the other end may be
        """
        if AssociationTypeMappings.__instance is None:
            AssociationTypeMappings()

        def _first(values):
            return values[0] if values else None

        results = []
        for mapping in AssociationTypeMappings.__instance.mappings:
            categories = list(mapping.category or [])
            category = _first(categories)
            # Check if entity can be the subject
            if mapping.subject_category and entity_category in mapping.subject_category:
                results.append(
                    {
                        "key": mapping.key,
                        "category": category,
                        "categories": categories,
                        "label": mapping.subject_label or category,
                        "context_field": "subject",
                        "target_category": _first(mapping.object_category),
                        "target_categories": list(mapping.object_category or []),
                    }
                )
            # Check if entity can be the object (reverse traversal)
            if mapping.object_category and entity_category in mapping.object_category:
                results.append(
                    {
                        "key": mapping.key,
                        "category": category,
                        "categories": categories,
                        "label": mapping.object_label or category,
                        "context_field": "object",
                        "target_category": _first(mapping.subject_category),
                        "target_categories": list(mapping.subject_category or []),
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
            # default to category-only matching, which is what every legacy section needs
            if not entry.get("match_criteria"):
                entry["match_criteria"] = MatchCriteriaEnum.category.value
        adapter = TypeAdapter(List[AssociationTypeMapping])
        mappings = adapter.validate_python(mapping_data)
        try:
            self._validate(mappings)
        except ValueError:
            # Drop the singleton so a later get_mappings() re-runs this and raises again.
            # Publishing self.mappings first would mean the very next call sailed past the
            # check and served the invalid config for the life of the process.
            AssociationTypeMappings.__instance = None
            raise
        self.mappings = mappings

    @staticmethod
    def _validate(mappings: List[AssociationTypeMapping]) -> None:
        """Reject configurations that fail silently at runtime rather than loudly here."""
        keys = [m.key for m in mappings]
        duplicate_keys = sorted({key for key in keys if keys.count(key) > 1})
        if duplicate_keys:
            # Two sections sharing a key merge their counts, and one wins the table lookup.
            # Easy to introduce now that `key` defaults to the first of several categories.
            raise ValueError(f"Duplicate association-type section keys in yaml: {duplicate_keys}")

        fragments = {}
        for mapping in mappings:
            fragment = get_solr_query_fragment(mapping)
            if not fragment:
                # `category` is no longer required, so a mapping can declare no criteria at
                # all. Its fragment is empty, which would be interpolated into every
                # entity's counts query as `(None) AND subject:"..."` and break the whole
                # request, not just that section.
                raise ValueError(f"Association-type section {mapping.key!r} declares no match criteria")
            if fragment in fragments:
                # Counts are attributed by rebuilding each mapping's fragment and looking it
                # up in the Solr response, which is keyed by query string. Two sections with
                # identical fragments collapse to one and the other silently vanishes from
                # the node page.
                raise ValueError(
                    f"Association-type sections {fragments[fragment]!r} and {mapping.key!r} "
                    f"produce the same Solr query: {fragment}"
                )
            fragments[fragment] = mapping.key


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


def uses_full_criteria(agm: AssociationTypeMapping) -> bool:
    """Whether a section matches on all its declared criteria (predicate /
    subject_category / object_category / source), rather than category alone.

    Read from the mapping's explicit `match_criteria`, which defaults to `category`.
    Legacy single-category sections declare subject/object_category only as entity-grid
    direction metadata; matching on those as Solr criteria would undercount edges whose
    node categories differ from the declared ones (e.g. gene-expression edges whose object
    is biolink:NamedThing, which cost GeneToExpressionSite -83% when this was briefly the
    default). Sections that cannot be identified by category alone — the LOINC sections,
    whose edges all share biolink:Association — set `match_criteria: full`.

    This used to be inferred from `agm.key not in agm.category`, i.e. from whether the
    author happened to give the section a key. That made an invisible behavioural switch
    out of a field people set for URL and UI reasons, and a section could lose the opt-in
    simply by being merged from a branch that predated it.
    """
    return agm.match_criteria == MatchCriteriaEnum.full


def get_solr_query_fragment(agm: AssociationTypeMapping) -> str:
    """Build the Solr clause that selects this association type: AND across the
    present criteria, each criterion OR'd internally. Legacy single-category
    sections match on category alone (see uses_full_criteria)."""
    if not uses_full_criteria(agm):
        return _or_group("category", agm.category)
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
    additional filters. Legacy single-category sections contribute no extra
    criteria (see uses_full_criteria).
    """
    if not uses_full_criteria(agm):
        return []
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
    """SQL equivalent of get_solr_query_fragment (AND across criteria, OR within).
    Legacy single-category sections match on category alone (see
    uses_full_criteria)."""

    def _or_group_sql(field, values):
        if not values:
            return None
        if isinstance(values, str):
            values = [values]
        if len(values) == 1:
            return f'{field} = "{values[0]}"'
        return "(" + " OR ".join(f'{field} = "{value}"' for value in values) + ")"

    if not uses_full_criteria(agm):
        return _or_group_sql("category", agm.category)

    parts = [
        _or_group_sql("category", agm.category),
        _or_group_sql("predicate", agm.predicate),
        _or_group_sql("subject_category", agm.subject_category),
        _or_group_sql("object_category", agm.object_category),
        _or_group_sql("primary_knowledge_source", agm.primary_knowledge_source),
        _or_group_sql("provided_by", agm.provided_by),
    ]
    return " AND ".join(part for part in parts if part)
