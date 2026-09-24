"""Which entity fields an endpoint asks Solr for.

`Entity` and `SearchResult` declare the same fields (bar `score`), so search and
grounding share one definition of what is bulk and what is not.
"""

from monarch_py.datamodels.model import Entity

# The two field groups that make an entity response large. On the 09-02 index these are
# ~69% and ~33% of an ~793KB search response, while every other field in the model put
# together is about 1%. They are bulk annotations on the entity, not anything a result
# list or a grounding match displays, so they are opt-in rather than default.
PHENOTYPE_FIELDS = [
    "has_phenotype",
    "has_phenotype_label",
    "has_phenotype_count",
    "has_phenotype_closure",
    "has_phenotype_closure_label",
]
DESCENDANT_FIELDS = [
    "has_descendant",
    "has_descendant_label",
    "has_descendant_count",
]


def entity_fields(include_phenotypes: bool = False, include_descendants: bool = False) -> str:
    """The Solr field list for an entity result, as a comma-separated string.

    Derived from the model rather than hard-coded so a field added to it is returned by
    default instead of silently going missing. Solr ignores names that are not in the
    schema, so a model field with no matching Solr field is harmless.

    Everything except the two bulk groups is returned by default: together they are
    almost the entire payload, while the remaining fields cost about 1%, so there is
    nothing to gain by dropping them and a caller to break by doing so.
    """
    excluded = set()
    if not include_phenotypes:
        excluded.update(PHENOTYPE_FIELDS)
    if not include_descendants:
        excluded.update(DESCENDANT_FIELDS)
    # `score` is a Solr pseudo-field rather than a stored one, and an unrestricted `fl`
    # does not return it today; listing it would start populating it.
    excluded.add("score")
    return ",".join(field for field in Entity.model_fields if field not in excluded)
