from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel as BaseModel
from pydantic import Field

metamodel_version = "None"
version = "None"


class WeakRefShimBaseModel(BaseModel):
    __slots__ = "__weakref__"


class ConfiguredBaseModel(
    WeakRefShimBaseModel,
    validate_assignment=True,
    validate_all=True,
    underscore_attrs_are_private=True,
    extra="forbid",
    arbitrary_types_allowed=True,
):
    pass


class Node(ConfiguredBaseModel):

    id: str = Field(None)
    label: Optional[str] = Field(None)
    iri: Optional[str] = Field(None)
    category: Optional[str] = Field("monarch-api:Node")
    clinical_modifiers: Optional[str] = Field(None)
    replaced_by: Optional[str] = Field(None)
    deprecated: Optional[str] = Field(None)
    consider: Optional[str] = Field(None)
    xrefs: Optional[str] = Field(None)
    synonyms: Optional[List[Synonym]] = Field(default_factory=list)
    taxon: Optional[Taxon] = Field(None)
    inheritance: Optional[Inheritance] = Field(None)
    association_counts: Optional[List[AssociationCount]] = Field(default_factory=list)


class Inheritance(ConfiguredBaseModel):

    id: Optional[str] = Field(None)
    pred: Optional[str] = Field(None)
    xrefs: Optional[str] = Field(None)


class Synonym(ConfiguredBaseModel):

    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None)
    iri: Optional[str] = Field(None)


class Taxon(ConfiguredBaseModel):

    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None)


class AssociationCount(ConfiguredBaseModel):

    id: Optional[str] = Field(None)
    counts: Optional[str] = Field(None)
    counts_by_taxon: Optional[str] = Field(None)


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
Node.update_forward_refs()
Inheritance.update_forward_refs()
Synonym.update_forward_refs()
Taxon.update_forward_refs()
AssociationCount.update_forward_refs()
