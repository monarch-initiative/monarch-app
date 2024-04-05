from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, ConfigDict, Field, field_validator
import re
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )


class AssociationDirectionEnum(str, Enum):
    """
    The directionality of an association as it relates to a specified entity, with edges being categorized as incoming or outgoing
    """

    # An association for which a specified entity is the object or part of the object closure
    incoming = "incoming"
    # An association for which a specified entity is the subject or part of the subject closure
    outgoing = "outgoing"


class Association(ConfiguredBaseModel):

    id: str = Field(...)
    category: Optional[str] = Field(None)
    subject: str = Field(...)
    original_subject: Optional[str] = Field(None)
    subject_namespace: Optional[str] = Field(None, description="""The namespace/prefix of the subject entity""")
    subject_category: Optional[str] = Field(None, description="""The category of the subject entity""")
    subject_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing subject id and the ids of all of it's ancestors"""
    )
    subject_label: Optional[str] = Field(None, description="""The name of the subject entity""")
    subject_closure_label: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing subject name and the names of all of it's ancestors"""
    )
    subject_taxon: Optional[str] = Field(None)
    subject_taxon_label: Optional[str] = Field(None)
    predicate: str = Field(...)
    object: str = Field(...)
    original_object: Optional[str] = Field(None)
    object_namespace: Optional[str] = Field(None, description="""The namespace/prefix of the object entity""")
    object_category: Optional[str] = Field(None, description="""The category of the object entity""")
    object_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing object id and the ids of all of it's ancestors"""
    )
    object_label: Optional[str] = Field(None, description="""The name of the object entity""")
    object_closure_label: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing object name and the names of all of it's ancestors"""
    )
    object_taxon: Optional[str] = Field(None)
    object_taxon_label: Optional[str] = Field(None)
    primary_knowledge_source: Optional[str] = Field(None)
    aggregator_knowledge_source: Optional[List[str]] = Field(default_factory=list)
    negated: Optional[bool] = Field(None)
    pathway: Optional[str] = Field(None)
    evidence_count: Optional[int] = Field(
        None, description="""count of supporting documents, evidence codes, and sources supplying evidence"""
    )
    knowledge_level: Optional[str] = Field(
        None,
        description="""Describes the level of knowledge expressed in a statement, based on the reasoning or analysis methods used to generate the statement, or the scope or specificity of what the statement expresses to be true.""",
    )
    agent_type: Optional[str] = Field(
        None,
        description="""Describes the high-level category of agent who originally generated a  statement of knowledge or other type of information.""",
    )
    has_evidence: Optional[List[str]] = Field(default_factory=list)
    has_evidence_links: Optional[List[ExpandedCurie]] = Field(
        default_factory=list, description="""List of ExpandedCuries with id and url for evidence"""
    )
    has_count: Optional[int] = Field(None, description="""count of out of has_total representing a frequency""")
    has_total: Optional[int] = Field(None, description="""total, devided by has_count, representing a frequency""")
    has_percentage: Optional[float] = Field(
        None,
        description="""percentage, which may be calculated from has_count and has_total, as 100 * quotient or provided directly, rounded to the integer level""",
    )
    has_quotient: Optional[float] = Field(None, description="""quotient, which should be 1/100 of has_percentage""")
    grouping_key: Optional[str] = Field(
        None,
        description="""A concatenation of fields used to group associations with the same essential/defining properties""",
    )
    provided_by: Optional[str] = Field(None)
    provided_by_link: Optional[ExpandedCurie] = Field(
        None, description="""A link to the docs for the knowledge source that provided the node/edge."""
    )
    publications: Optional[List[str]] = Field(default_factory=list)
    publications_links: Optional[List[ExpandedCurie]] = Field(
        default_factory=list, description="""List of ExpandedCuries with id and url for publications"""
    )
    frequency_qualifier: Optional[str] = Field(None)
    onset_qualifier: Optional[str] = Field(None)
    sex_qualifier: Optional[str] = Field(None)
    stage_qualifier: Optional[str] = Field(None)
    qualifiers: Optional[List[str]] = Field(default_factory=list)
    qualifiers_label: Optional[str] = Field(None, description="""The name of the frequency_qualifier entity""")
    qualifiers_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the frequency_qualifier entity"""
    )
    qualifiers_category: Optional[str] = Field(None, description="""The category of the frequency_qualifier entity""")
    qualifiers_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier id and the ids of all of it's ancestors""",
    )
    qualifiers_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier name and the names of all of it's ancestors""",
    )
    qualifier: Optional[List[str]] = Field(default_factory=list)
    qualifier_label: Optional[str] = Field(None, description="""The name of the frequency_qualifier entity""")
    qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the frequency_qualifier entity"""
    )
    qualifier_category: Optional[str] = Field(None, description="""The category of the frequency_qualifier entity""")
    qualifier_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier id and the ids of all of it's ancestors""",
    )
    qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier name and the names of all of it's ancestors""",
    )
    frequency_qualifier_label: Optional[str] = Field(None, description="""The name of the frequency_qualifier entity""")
    frequency_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the frequency_qualifier entity"""
    )
    frequency_qualifier_category: Optional[str] = Field(
        None, description="""The category of the frequency_qualifier entity"""
    )
    frequency_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier id and the ids of all of it's ancestors""",
    )
    frequency_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier name and the names of all of it's ancestors""",
    )
    onset_qualifier_label: Optional[str] = Field(None, description="""The name of the onset_qualifier entity""")
    onset_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the onset_qualifier entity"""
    )
    onset_qualifier_category: Optional[str] = Field(None, description="""The category of the onset_qualifier entity""")
    onset_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing onset_qualifier id and the ids of all of it's ancestors"""
    )
    onset_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing onset_qualifier name and the names of all of it's ancestors""",
    )
    sex_qualifier_label: Optional[str] = Field(None, description="""The name of the sex_qualifier entity""")
    sex_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the sex_qualifier entity"""
    )
    sex_qualifier_category: Optional[str] = Field(None, description="""The category of the sex_qualifier entity""")
    sex_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing sex_qualifier id and the ids of all of it's ancestors"""
    )
    sex_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing sex_qualifier name and the names of all of it's ancestors""",
    )
    stage_qualifier_label: Optional[str] = Field(None, description="""The name of the stage_qualifier entity""")
    stage_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the stage_qualifier entity"""
    )
    stage_qualifier_category: Optional[str] = Field(None, description="""The category of the stage_qualifier entity""")
    stage_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing stage_qualifier id and the ids of all of it's ancestors"""
    )
    stage_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing stage_qualifier name and the names of all of it's ancestors""",
    )


class AssociationCountList(ConfiguredBaseModel):
    """
    Container class for a list of association counts
    """

    items: List[AssociationCount] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )


class CompactAssociation(ConfiguredBaseModel):

    category: Optional[str] = Field(None)
    subject: str = Field(...)
    subject_label: Optional[str] = Field(None, description="""The name of the subject entity""")
    predicate: str = Field(...)
    object: str = Field(...)
    object_label: Optional[str] = Field(None, description="""The name of the object entity""")
    negated: Optional[bool] = Field(None)


class AssociationTypeMapping(ConfiguredBaseModel):
    """
    A data class to hold the necessary information to produce association type counts for given  entities with appropriate directional labels
    """

    subject_label: Optional[str] = Field(
        None, description="""A label to describe the subjects of the association type as a whole for use in the UI"""
    )
    object_label: Optional[str] = Field(
        None, description="""A label to describe the objects of the association type as a whole for use in the UI"""
    )
    symmetric: bool = Field(
        False,
        description="""Whether the association type is symmetric, meaning that the subject and object labels should be interchangeable""",
    )
    category: str = Field(..., description="""The biolink category to use in queries for this association type""")


class DirectionalAssociation(Association):
    """
    An association that gives it's direction relative to a specified entity
    """

    direction: AssociationDirectionEnum = Field(
        ...,
        description="""The directionality of the association relative to a given entity for an association_count. If the entity is the subject or in the subject closure, the direction is forwards, if it is the object or in the object closure, the direction is backwards.""",
    )
    id: str = Field(...)
    category: Optional[str] = Field(None)
    subject: str = Field(...)
    original_subject: Optional[str] = Field(None)
    subject_namespace: Optional[str] = Field(None, description="""The namespace/prefix of the subject entity""")
    subject_category: Optional[str] = Field(None, description="""The category of the subject entity""")
    subject_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing subject id and the ids of all of it's ancestors"""
    )
    subject_label: Optional[str] = Field(None, description="""The name of the subject entity""")
    subject_closure_label: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing subject name and the names of all of it's ancestors"""
    )
    subject_taxon: Optional[str] = Field(None)
    subject_taxon_label: Optional[str] = Field(None)
    predicate: str = Field(...)
    object: str = Field(...)
    original_object: Optional[str] = Field(None)
    object_namespace: Optional[str] = Field(None, description="""The namespace/prefix of the object entity""")
    object_category: Optional[str] = Field(None, description="""The category of the object entity""")
    object_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing object id and the ids of all of it's ancestors"""
    )
    object_label: Optional[str] = Field(None, description="""The name of the object entity""")
    object_closure_label: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing object name and the names of all of it's ancestors"""
    )
    object_taxon: Optional[str] = Field(None)
    object_taxon_label: Optional[str] = Field(None)
    primary_knowledge_source: Optional[str] = Field(None)
    aggregator_knowledge_source: Optional[List[str]] = Field(default_factory=list)
    negated: Optional[bool] = Field(None)
    pathway: Optional[str] = Field(None)
    evidence_count: Optional[int] = Field(
        None, description="""count of supporting documents, evidence codes, and sources supplying evidence"""
    )
    knowledge_level: Optional[str] = Field(
        None,
        description="""Describes the level of knowledge expressed in a statement, based on the reasoning or analysis methods used to generate the statement, or the scope or specificity of what the statement expresses to be true.""",
    )
    agent_type: Optional[str] = Field(
        None,
        description="""Describes the high-level category of agent who originally generated a  statement of knowledge or other type of information.""",
    )
    has_evidence: Optional[List[str]] = Field(default_factory=list)
    has_evidence_links: Optional[List[ExpandedCurie]] = Field(
        default_factory=list, description="""List of ExpandedCuries with id and url for evidence"""
    )
    has_count: Optional[int] = Field(None, description="""count of out of has_total representing a frequency""")
    has_total: Optional[int] = Field(None, description="""total, devided by has_count, representing a frequency""")
    has_percentage: Optional[float] = Field(
        None,
        description="""percentage, which may be calculated from has_count and has_total, as 100 * quotient or provided directly, rounded to the integer level""",
    )
    has_quotient: Optional[float] = Field(None, description="""quotient, which should be 1/100 of has_percentage""")
    grouping_key: Optional[str] = Field(
        None,
        description="""A concatenation of fields used to group associations with the same essential/defining properties""",
    )
    provided_by: Optional[str] = Field(None)
    provided_by_link: Optional[ExpandedCurie] = Field(
        None, description="""A link to the docs for the knowledge source that provided the node/edge."""
    )
    publications: Optional[List[str]] = Field(default_factory=list)
    publications_links: Optional[List[ExpandedCurie]] = Field(
        default_factory=list, description="""List of ExpandedCuries with id and url for publications"""
    )
    frequency_qualifier: Optional[str] = Field(None)
    onset_qualifier: Optional[str] = Field(None)
    sex_qualifier: Optional[str] = Field(None)
    stage_qualifier: Optional[str] = Field(None)
    qualifiers: Optional[List[str]] = Field(default_factory=list)
    qualifiers_label: Optional[str] = Field(None, description="""The name of the frequency_qualifier entity""")
    qualifiers_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the frequency_qualifier entity"""
    )
    qualifiers_category: Optional[str] = Field(None, description="""The category of the frequency_qualifier entity""")
    qualifiers_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier id and the ids of all of it's ancestors""",
    )
    qualifiers_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier name and the names of all of it's ancestors""",
    )
    qualifier: Optional[List[str]] = Field(default_factory=list)
    qualifier_label: Optional[str] = Field(None, description="""The name of the frequency_qualifier entity""")
    qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the frequency_qualifier entity"""
    )
    qualifier_category: Optional[str] = Field(None, description="""The category of the frequency_qualifier entity""")
    qualifier_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier id and the ids of all of it's ancestors""",
    )
    qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier name and the names of all of it's ancestors""",
    )
    frequency_qualifier_label: Optional[str] = Field(None, description="""The name of the frequency_qualifier entity""")
    frequency_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the frequency_qualifier entity"""
    )
    frequency_qualifier_category: Optional[str] = Field(
        None, description="""The category of the frequency_qualifier entity"""
    )
    frequency_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier id and the ids of all of it's ancestors""",
    )
    frequency_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing frequency_qualifier name and the names of all of it's ancestors""",
    )
    onset_qualifier_label: Optional[str] = Field(None, description="""The name of the onset_qualifier entity""")
    onset_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the onset_qualifier entity"""
    )
    onset_qualifier_category: Optional[str] = Field(None, description="""The category of the onset_qualifier entity""")
    onset_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing onset_qualifier id and the ids of all of it's ancestors"""
    )
    onset_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing onset_qualifier name and the names of all of it's ancestors""",
    )
    sex_qualifier_label: Optional[str] = Field(None, description="""The name of the sex_qualifier entity""")
    sex_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the sex_qualifier entity"""
    )
    sex_qualifier_category: Optional[str] = Field(None, description="""The category of the sex_qualifier entity""")
    sex_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing sex_qualifier id and the ids of all of it's ancestors"""
    )
    sex_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing sex_qualifier name and the names of all of it's ancestors""",
    )
    stage_qualifier_label: Optional[str] = Field(None, description="""The name of the stage_qualifier entity""")
    stage_qualifier_namespace: Optional[str] = Field(
        None, description="""The namespace/prefix of the stage_qualifier entity"""
    )
    stage_qualifier_category: Optional[str] = Field(None, description="""The category of the stage_qualifier entity""")
    stage_qualifier_closure: Optional[List[str]] = Field(
        default_factory=list, description="""Field containing stage_qualifier id and the ids of all of it's ancestors"""
    )
    stage_qualifier_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""Field containing stage_qualifier name and the names of all of it's ancestors""",
    )


class ExpandedCurie(ConfiguredBaseModel):
    """
    A curie bundled along with its expanded url
    """

    id: str = Field(...)
    url: Optional[str] = Field(None)


class Entity(ConfiguredBaseModel):
    """
    Represents an Entity in the Monarch KG data model
    """

    id: str = Field(...)
    category: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    full_name: Optional[str] = Field(None, description="""The long form name of an entity""")
    deprecated: Optional[bool] = Field(
        None, description="""A boolean flag indicating that an entity is no longer considered current or valid."""
    )
    description: Optional[str] = Field(None)
    xref: Optional[List[str]] = Field(default_factory=list)
    provided_by: Optional[str] = Field(None)
    in_taxon: Optional[str] = Field(None, description="""The biolink taxon that the entity is in the closure of.""")
    in_taxon_label: Optional[str] = Field(
        None, description="""The label of the biolink taxon that the entity is in the closure of."""
    )
    symbol: Optional[str] = Field(None)
    synonym: Optional[List[str]] = Field(default_factory=list)
    uri: Optional[str] = Field(None, description="""The URI of the entity""")
    namespace: Optional[str] = Field(None, description="""The namespace/prefix portion of this entity's identifier""")
    has_phenotype: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype identifiers that are known to be associated with this entity""",
    )
    has_phenotype_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype labels that are known to be associated with this entity""",
    )
    has_phenotype_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""",
    )
    has_phenotype_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""",
    )
    has_phenotype_count: Optional[int] = Field(
        None, description="""A count of the number of phenotypes that are known to be associated with this entity"""
    )


class FacetValue(ConfiguredBaseModel):

    label: str = Field(...)
    count: Optional[int] = Field(None, description="""count of documents""")


class AssociationCount(FacetValue):

    category: Optional[str] = Field(None)
    label: str = Field(...)
    count: Optional[int] = Field(None, description="""count of documents""")


class FacetField(ConfiguredBaseModel):

    label: str = Field(...)
    facet_values: Optional[List[FacetValue]] = Field(
        default_factory=list, description="""Collection of FacetValue label/value instances belonging to a FacetField"""
    )


class HistoPheno(ConfiguredBaseModel):

    id: str = Field(...)
    items: List[HistoBin] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )


class HistoBin(FacetValue):

    id: str = Field(...)
    label: str = Field(...)
    count: Optional[int] = Field(None, description="""count of documents""")


class Mapping(ConfiguredBaseModel):
    """
    A minimal class to hold a SSSOM mapping
    """

    subject_id: str = Field(...)
    subject_label: Optional[str] = Field(None, description="""The name of the subject entity""")
    predicate_id: str = Field(...)
    object_id: str = Field(...)
    object_label: Optional[str] = Field(None, description="""The name of the object entity""")
    mapping_justification: Optional[str] = Field(None)
    id: str = Field(...)


class Node(Entity):
    """
    UI container class extending Entity with additional information
    """

    in_taxon: Optional[str] = Field(None, description="""The biolink taxon that the entity is in the closure of.""")
    in_taxon_label: Optional[str] = Field(
        None, description="""The label of the biolink taxon that the entity is in the closure of."""
    )
    inheritance: Optional[Entity] = Field(None)
    causal_gene: Optional[List[Entity]] = Field(
        default_factory=list, description="""A list of genes that are known to be causally associated with a disease"""
    )
    causes_disease: Optional[List[Entity]] = Field(
        default_factory=list, description="""A list of diseases that are known to be causally associated with a gene"""
    )
    mappings: Optional[List[ExpandedCurie]] = Field(
        default_factory=list, description="""List of ExpandedCuries with id and url for mapped entities"""
    )
    external_links: Optional[List[ExpandedCurie]] = Field(
        default_factory=list, description="""ExpandedCurie with id and url for xrefs"""
    )
    provided_by_link: Optional[ExpandedCurie] = Field(
        None, description="""A link to the docs for the knowledge source that provided the node/edge."""
    )
    association_counts: List[AssociationCount] = Field(default_factory=list)
    node_hierarchy: Optional[NodeHierarchy] = Field(None)
    id: str = Field(...)
    category: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    full_name: Optional[str] = Field(None, description="""The long form name of an entity""")
    deprecated: Optional[bool] = Field(
        None, description="""A boolean flag indicating that an entity is no longer considered current or valid."""
    )
    description: Optional[str] = Field(None)
    xref: Optional[List[str]] = Field(default_factory=list)
    provided_by: Optional[str] = Field(None)
    symbol: Optional[str] = Field(None)
    synonym: Optional[List[str]] = Field(default_factory=list)
    uri: Optional[str] = Field(None, description="""The URI of the entity""")
    namespace: Optional[str] = Field(None, description="""The namespace/prefix portion of this entity's identifier""")
    has_phenotype: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype identifiers that are known to be associated with this entity""",
    )
    has_phenotype_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype labels that are known to be associated with this entity""",
    )
    has_phenotype_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""",
    )
    has_phenotype_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""",
    )
    has_phenotype_count: Optional[int] = Field(
        None, description="""A count of the number of phenotypes that are known to be associated with this entity"""
    )


class NodeHierarchy(ConfiguredBaseModel):

    super_classes: List[Entity] = Field(default_factory=list)
    sub_classes: List[Entity] = Field(default_factory=list)


class Release(ConfiguredBaseModel):
    """
    A class to hold information about a release of the Monarch KG
    """

    version: Optional[str] = Field(None)
    url: Optional[str] = Field(None)
    kg: Optional[str] = Field(None)
    sqlite: Optional[str] = Field(None)
    solr: Optional[str] = Field(None)
    neo4j: Optional[str] = Field(None)
    metadata: Optional[str] = Field(None)
    graph_stats: Optional[str] = Field(None)
    qc_report: Optional[str] = Field(None)


class Results(ConfiguredBaseModel):

    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class AssociationResults(Results):

    items: List[Association] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class CompactAssociationResults(Results):

    items: List[CompactAssociation] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class AssociationTableResults(Results):

    items: List[DirectionalAssociation] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class CategoryGroupedAssociationResults(Results):

    counterpart_category: Optional[str] = Field(
        None,
        description="""The category of the counterpart entity in a given association,  eg. the category of the entity that is not the subject""",
    )
    items: List[Association] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class EntityResults(Results):

    items: List[Entity] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class MappingResults(Results):
    """
    SSSOM Mappings returned as a results collection
    """

    items: List[Mapping] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class MultiEntityAssociationResults(Results):

    id: str = Field(...)
    name: Optional[str] = Field(None)
    associated_categories: List[CategoryGroupedAssociationResults] = Field(default_factory=list)
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class SearchResult(Entity):

    highlight: Optional[str] = Field(None, description="""matching text snippet containing html tags""")
    score: Optional[float] = Field(None)
    id: str = Field(...)
    category: str = Field(...)
    name: str = Field(...)
    full_name: Optional[str] = Field(None, description="""The long form name of an entity""")
    deprecated: Optional[bool] = Field(
        None, description="""A boolean flag indicating that an entity is no longer considered current or valid."""
    )
    description: Optional[str] = Field(None)
    xref: Optional[List[str]] = Field(default_factory=list)
    provided_by: Optional[str] = Field(None)
    in_taxon: Optional[str] = Field(None, description="""The biolink taxon that the entity is in the closure of.""")
    in_taxon_label: Optional[str] = Field(
        None, description="""The label of the biolink taxon that the entity is in the closure of."""
    )
    symbol: Optional[str] = Field(None)
    synonym: Optional[List[str]] = Field(default_factory=list)
    uri: Optional[str] = Field(None, description="""The URI of the entity""")
    namespace: Optional[str] = Field(None, description="""The namespace/prefix portion of this entity's identifier""")
    has_phenotype: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype identifiers that are known to be associated with this entity""",
    )
    has_phenotype_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype labels that are known to be associated with this entity""",
    )
    has_phenotype_closure: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""",
    )
    has_phenotype_closure_label: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""",
    )
    has_phenotype_count: Optional[int] = Field(
        None, description="""A count of the number of phenotypes that are known to be associated with this entity"""
    )


class SearchResults(Results):

    items: List[SearchResult] = Field(
        default_factory=list, description="""A collection of items, with the type to be overriden by slot_usage"""
    )
    facet_fields: Optional[List[FacetField]] = Field(
        default_factory=list, description="""Collection of facet field responses with the field values and counts"""
    )
    facet_queries: Optional[List[FacetValue]] = Field(
        default_factory=list,
        description="""Collection of facet query responses with the query string values and counts""",
    )
    limit: int = Field(..., description="""number of items to return in a response""")
    offset: int = Field(..., description="""offset into the total number of items""")
    total: int = Field(..., description="""total number of items matching a query""")


class TextAnnotationResult(ConfiguredBaseModel):

    text: Optional[str] = Field(None, description="""text without tokens""")
    tokens: Optional[List[Entity]] = Field(default_factory=list, description="""A collection of entities or concepts""")
    start: Optional[int] = Field(None, description="""start position of the annotation""")
    end: Optional[int] = Field(None, description="""end position of the annotation""")


class PairwiseSimilarity(ConfiguredBaseModel):
    """
    Abstract grouping for representing individual pairwise similarities
    """

    None


class TermPairwiseSimilarity(PairwiseSimilarity):
    """
    A simple pairwise similarity between two atomic concepts/terms
    """

    subject_id: str = Field(...)
    subject_label: Optional[str] = Field(None, description="""The name of the subject entity""")
    subject_source: Optional[str] = Field(None, description="""the source for the first entity""")
    object_id: str = Field(...)
    object_label: Optional[str] = Field(None, description="""The name of the object entity""")
    object_source: Optional[str] = Field(None, description="""the source for the second entity""")
    ancestor_id: Optional[str] = Field(
        None,
        description="""the most recent common ancestor of the two compared entities. If there are multiple MRCAs then the most informative one is selected""",
    )
    ancestor_label: Optional[str] = Field(None, description="""the name or label of the ancestor concept""")
    ancestor_source: Optional[str] = Field(None)
    object_information_content: Optional[float] = Field(None, description="""The IC of the object""")
    subject_information_content: Optional[float] = Field(None, description="""The IC of the subject""")
    ancestor_information_content: Optional[float] = Field(None, description="""The IC of the object""")
    jaccard_similarity: Optional[float] = Field(
        None, description="""The number of concepts in the intersection divided by the number in the union"""
    )
    cosine_similarity: Optional[float] = Field(
        None, description="""the dot product of two node embeddings divided by the product of their lengths"""
    )
    dice_similarity: Optional[float] = Field(None)
    phenodigm_score: Optional[float] = Field(
        None, description="""the geometric mean of the jaccard similarity and the information content"""
    )


class TermSetPairwiseSimilarity(PairwiseSimilarity):
    """
    A simple pairwise similarity between two sets of concepts/terms
    """

    subject_termset: Optional[Dict[str, TermInfo]] = Field(default_factory=dict)
    object_termset: Optional[Dict[str, TermInfo]] = Field(default_factory=dict)
    subject_best_matches: Optional[Dict[str, BestMatch]] = Field(default_factory=dict)
    object_best_matches: Optional[Dict[str, BestMatch]] = Field(default_factory=dict)
    average_score: Optional[float] = Field(None)
    best_score: Optional[float] = Field(None)
    metric: Optional[str] = Field(None)


class TermInfo(ConfiguredBaseModel):

    id: str = Field(...)
    label: Optional[str] = Field(None)


class BestMatch(ConfiguredBaseModel):

    match_source: str = Field(...)
    match_source_label: Optional[str] = Field(None)
    match_target: Optional[str] = Field(None, description="""the entity matches""")
    match_target_label: Optional[str] = Field(None)
    score: float = Field(...)
    match_subsumer: Optional[str] = Field(None)
    match_subsumer_label: Optional[str] = Field(None)
    similarity: TermPairwiseSimilarity = Field(...)


class SemsimSearchResult(ConfiguredBaseModel):

    subject: Entity = Field(...)
    score: Optional[float] = Field(None)
    similarity: Optional[TermSetPairwiseSimilarity] = Field(None)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Association.model_rebuild()
AssociationCountList.model_rebuild()
CompactAssociation.model_rebuild()
AssociationTypeMapping.model_rebuild()
DirectionalAssociation.model_rebuild()
ExpandedCurie.model_rebuild()
Entity.model_rebuild()
FacetValue.model_rebuild()
AssociationCount.model_rebuild()
FacetField.model_rebuild()
HistoPheno.model_rebuild()
HistoBin.model_rebuild()
Mapping.model_rebuild()
Node.model_rebuild()
NodeHierarchy.model_rebuild()
Release.model_rebuild()
Results.model_rebuild()
AssociationResults.model_rebuild()
CompactAssociationResults.model_rebuild()
AssociationTableResults.model_rebuild()
CategoryGroupedAssociationResults.model_rebuild()
EntityResults.model_rebuild()
MappingResults.model_rebuild()
MultiEntityAssociationResults.model_rebuild()
SearchResult.model_rebuild()
SearchResults.model_rebuild()
TextAnnotationResult.model_rebuild()
PairwiseSimilarity.model_rebuild()
TermPairwiseSimilarity.model_rebuild()
TermSetPairwiseSimilarity.model_rebuild()
TermInfo.model_rebuild()
BestMatch.model_rebuild()
SemsimSearchResult.model_rebuild()
