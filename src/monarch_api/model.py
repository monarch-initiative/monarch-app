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


class Taxon(ConfiguredBaseModel):

    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None)


class AssociationCount(ConfiguredBaseModel):

    label: Optional[str] = Field(None)
    count: Optional[int] = Field(None)


class NodeHierarchy(ConfiguredBaseModel):

    super_classes: Optional[List[Entity]] = Field(default_factory=list)
    equivalent_classes: Optional[List[Entity]] = Field(default_factory=list)
    sub_classes: Optional[List[Entity]] = Field(default_factory=list)


class Association(ConfiguredBaseModel):

    aggregator_knowledge_source: Optional[List[str]] = Field(default_factory=list)
    id: Optional[str] = Field(None)
    subject: Optional[str] = Field(None)
    original_subject: Optional[str] = Field(None)
    subject_namespace: Optional[str] = Field(None)
    subject_category: Optional[List[str]] = Field(default_factory=list)
    subject_closure: Optional[List[str]] = Field(default_factory=list)
    subject_label: Optional[str] = Field(None)
    subject_closure_label: Optional[List[str]] = Field(default_factory=list)
    predicate: Optional[str] = Field(None)
    object: Optional[str] = Field(None)
    original_object: Optional[str] = Field(None)
    object_namespace: Optional[str] = Field(None)
    object_category: Optional[List[str]] = Field(default_factory=list)
    object_closure: Optional[List[str]] = Field(default_factory=list)
    object_label: Optional[str] = Field(None)
    object_closure_label: Optional[List[str]] = Field(default_factory=list)
    knowledge_source: Optional[List[str]] = Field(default_factory=list)
    primary_knowledge_source: Optional[List[str]] = Field(default_factory=list)
    category: Optional[List[str]] = Field(default_factory=list)
    negated: Optional[bool] = Field(None)
    provided_by: Optional[str] = Field(None)
    publications: Optional[List[str]] = Field(default_factory=list)
    qualifiers: Optional[List[str]] = Field(default_factory=list)
    frequency_qualifier: Optional[str] = Field(None)
    has_evidence: Optional[str] = Field(None)
    onset_qualifier: Optional[str] = Field(None)
    sex_qualifier: Optional[str] = Field(None)
    source: Optional[str] = Field(None)
    stage_qualifier: Optional[str] = Field(None)
    pathway: Optional[str] = Field(None)
    relation: Optional[str] = Field(None)


class Entity(ConfiguredBaseModel):

    id: Optional[str] = Field(None)
    category: Optional[List[str]] = Field(default_factory=list)
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    xref: Optional[List[str]] = Field(default_factory=list)
    provided_by: Optional[str] = Field(None)
    in_taxon: Optional[str] = Field(None)
    source: Optional[str] = Field(None)
    symbol: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    synonym: Optional[List[str]] = Field(default_factory=list)


class Node(Entity):

    taxon: Optional[Taxon] = Field(None)
    inheritance: Optional[Entity] = Field(None)
    association_counts: Optional[List[AssociationCount]] = Field(default_factory=list)
    node_hierarchy: Optional[NodeHierarchy] = Field(None)
    id: str = Field(None)
    category: Optional[List[str]] = Field(default_factory=list)
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    xref: Optional[List[str]] = Field(default_factory=list)
    provided_by: Optional[str] = Field(None)
    in_taxon: Optional[str] = Field(None)
    source: Optional[str] = Field(None)
    symbol: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    synonym: Optional[List[str]] = Field(default_factory=list)


class Results(ConfiguredBaseModel):

    limit: Optional[int] = Field(None)
    offset: Optional[int] = Field(None)
    total: Optional[int] = Field(None)


class AssociationResults(Results):

    associations: Optional[List[Association]] = Field(default_factory=list)
    limit: Optional[int] = Field(None)
    offset: Optional[int] = Field(None)
    total: Optional[int] = Field(None)


class EntityResults(Results):

    entities: Optional[List[Entity]] = Field(default_factory=list)
    limit: Optional[int] = Field(None)
    offset: Optional[int] = Field(None)
    total: Optional[int] = Field(None)


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
Taxon.update_forward_refs()
AssociationCount.update_forward_refs()
NodeHierarchy.update_forward_refs()
Association.update_forward_refs()
Entity.update_forward_refs()
Node.update_forward_refs()
Results.update_forward_refs()
AssociationResults.update_forward_refs()
EntityResults.update_forward_refs()
