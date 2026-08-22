"""Named filter bundles for `/search`.

A scope is a shorthand for the filters a caller would otherwise have to assemble from
knowledge of biolink categories, ontology namespaces and subset names. Grounding human
clinical text is the motivating case: `category=biolink:PhenotypicFeature` alone searches a
pool that is ~88% non-human (ZP, XPO, MP, FYPO...), and `category=biolink:Disease` alone
includes the VeNom veterinary terms.

Each scope is a promise about meaning, so changing what one covers is a silent behaviour
change for every caller using it. Keep the vocabulary small, and prefer adding a new scope
over redefining an existing one.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class SearchScope(str, Enum):
    """The named filter bundles `/search?scope=` accepts."""

    HUMAN_DISEASE = "human_disease"
    HUMAN_PHENOTYPE = "human_phenotype"
    HUMAN_GENE = "human_gene"
    RARE_DISEASE = "rare_disease"

    def __str__(self):
        return self.value


# The axes a scope can supply. `resolve_scope` also carries through axes no scope sets
# (exclude_namespace, in_taxon_label) so that what is echoed to the caller is the complete
# set of filters applied, not just the ones a scope had an opinion about.
SCOPED_AXES = ("category", "namespace", "subset", "exclude_subset", "in_taxon")


@dataclass(frozen=True)
class ScopeDefinition:
    """The filters a scope expands to. Empty lists mean "this scope says nothing about
    that axis", which is what lets an explicit parameter override one axis without
    discarding the rest of the bundle."""

    description: str
    category: List[str] = field(default_factory=list)
    namespace: List[str] = field(default_factory=list)
    subset: List[str] = field(default_factory=list)
    exclude_subset: List[str] = field(default_factory=list)
    in_taxon: List[str] = field(default_factory=list)


# VeNom terms are MONDO terms, so `namespace=MONDO` does not exclude them and both filters
# are needed: category:Disease is 36,082 MONDO + 180 MPATH, and dropping venom_* takes the
# MONDO side to 31,037.
SEARCH_SCOPES: Dict[SearchScope, ScopeDefinition] = {
    SearchScope.HUMAN_DISEASE: ScopeDefinition(
        description="Human diseases: MONDO, minus the VeNom veterinary subsets.",
        category=["biolink:Disease"],
        namespace=["MONDO"],
        exclude_subset=["venom_*"],
    ),
    SearchScope.HUMAN_PHENOTYPE: ScopeDefinition(
        description="Human phenotypes: HP only, excluding the species-specific and "
        "cross-species phenotype ontologies that make up most of the category.",
        category=["biolink:PhenotypicFeature"],
        namespace=["HP"],
    ),
    SearchScope.HUMAN_GENE: ScopeDefinition(
        description="Human genes: HGNC, by taxon rather than namespace so that a gene "
        "recorded under another namespace still qualifies.",
        category=["biolink:Gene"],
        in_taxon=["NCBITaxon:9606"],
    ),
    SearchScope.RARE_DISEASE: ScopeDefinition(
        description="Human diseases marked rare by any of the contributing rare-disease resources.",
        category=["biolink:Disease"],
        namespace=["MONDO"],
        subset=["rare"],
        exclude_subset=["venom_*"],
    ),
}


def resolve_scope(scope, **explicit) -> dict:
    """Expand `scope` into filter arguments, letting explicit arguments win per axis.

    Returns the *effective* filters rather than the scope's raw definition, so what is
    echoed to the caller is what was actually applied. An explicit argument replaces the
    scope's value for that axis rather than intersecting with it — `scope=human_disease`
    plus `namespace=DOID` searches DOID diseases, it does not search nothing.
    """
    resolved = {axis: value for axis, value in explicit.items() if value}
    if scope is None:
        return resolved
    definition = SEARCH_SCOPES[SearchScope(scope)]
    for axis in SCOPED_AXES:
        if not resolved.get(axis):
            scoped = getattr(definition, axis)
            if scoped:
                resolved[axis] = list(scoped)
    return resolved
