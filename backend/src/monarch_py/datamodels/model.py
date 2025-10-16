from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "allow",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = None

class AssociationDirectionEnum(str, Enum):
    """
    The directionality of an association as it relates to a specified entity, with edges being categorized as incoming or outgoing
    """
    incoming = "incoming"
    """
    An association for which a specified entity is the object or part of the object closure
    """
    outgoing = "outgoing"
    """
    An association for which a specified entity is the subject or part of the subject closure
    """



class PairwiseSimilarity(ConfiguredBaseModel):
    """
    Abstract grouping for representing individual pairwise similarities
    """
    pass


class TermPairwiseSimilarity(PairwiseSimilarity):
    """
    A simple pairwise similarity between two atomic concepts/terms
    """
    subject_id: str = Field(default=...)
    subject_label: Optional[str] = Field(default=None, description="""The name of the subject entity""")
    subject_source: Optional[str] = Field(default=None, description="""the source for the first entity""")
    object_id: str = Field(default=...)
    object_label: Optional[str] = Field(default=None, description="""The name of the object entity""")
    object_source: Optional[str] = Field(default=None, description="""the source for the second entity""")
    ancestor_id: Optional[str] = Field(default=None, description="""the most recent common ancestor of the two compared entities. If there are multiple MRCAs then the most informative one is selected""")
    ancestor_label: Optional[str] = Field(default=None, description="""the name or label of the ancestor concept""")
    ancestor_source: Optional[str] = Field(default=None)
    object_information_content: Optional[float] = Field(default=None, description="""The IC of the object""")
    subject_information_content: Optional[float] = Field(default=None, description="""The IC of the subject""")
    ancestor_information_content: Optional[float] = Field(default=None, description="""The IC of the object""")
    jaccard_similarity: Optional[float] = Field(default=None, description="""The number of concepts in the intersection divided by the number in the union""")
    cosine_similarity: Optional[float] = Field(default=None, description="""the dot product of two node embeddings divided by the product of their lengths""")
    dice_similarity: Optional[float] = Field(default=None)
    phenodigm_score: Optional[float] = Field(default=None, description="""the geometric mean of the jaccard similarity and the information content""")


class TermSetPairwiseSimilarity(PairwiseSimilarity):
    """
    A simple pairwise similarity between two sets of concepts/terms
    """
    subject_termset: Optional[dict[str, Union[str, TermInfo]]] = Field(default=None)
    object_termset: Optional[dict[str, Union[str, TermInfo]]] = Field(default=None)
    subject_best_matches: Optional[dict[str, BestMatch]] = Field(default=None)
    object_best_matches: Optional[dict[str, BestMatch]] = Field(default=None)
    average_score: Optional[float] = Field(default=None)
    best_score: Optional[float] = Field(default=None)
    metric: Optional[str] = Field(default=None)


class TermInfo(ConfiguredBaseModel):
    id: str = Field(default=...)
    label: Optional[str] = Field(default=None)


class BestMatch(ConfiguredBaseModel):
    match_source: str = Field(default=...)
    match_source_label: Optional[str] = Field(default=None)
    match_target: Optional[str] = Field(default=None, description="""the entity matches""")
    match_target_label: Optional[str] = Field(default=None)
    score: float = Field(default=...)
    match_subsumer: Optional[str] = Field(default=None)
    match_subsumer_label: Optional[str] = Field(default=None)
    similarity: TermPairwiseSimilarity = Field(default=...)


class SemsimSearchResult(ConfiguredBaseModel):
    subject: Entity = Field(default=...)
    score: Optional[float] = Field(default=None)
    similarity: Optional[TermSetPairwiseSimilarity] = Field(default=None)


class Association(ConfiguredBaseModel):
    id: str = Field(default=...)
    category: Optional[str] = Field(default=None)
    subject: str = Field(default=...)
    original_subject: Optional[str] = Field(default=None)
    subject_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the subject entity""")
    subject_category: Optional[str] = Field(default=None, description="""The category of the subject entity""")
    subject_closure: Optional[list[str]] = Field(default=None, description="""Field containing subject id and the ids of all of it's ancestors""")
    subject_label: Optional[str] = Field(default=None, description="""The name of the subject entity""")
    subject_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing subject name and the names of all of it's ancestors""")
    subject_taxon: Optional[str] = Field(default=None)
    subject_taxon_label: Optional[str] = Field(default=None)
    predicate: str = Field(default=...)
    original_predicate: Optional[str] = Field(default=None, description="""used to hold the original relation/predicate that an external knowledge source uses before transformation to match the biolink-model specification.""")
    object: str = Field(default=...)
    original_object: Optional[str] = Field(default=None)
    object_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the object entity""")
    object_category: Optional[str] = Field(default=None, description="""The category of the object entity""")
    object_closure: Optional[list[str]] = Field(default=None, description="""Field containing object id and the ids of all of it's ancestors""")
    object_label: Optional[str] = Field(default=None, description="""The name of the object entity""")
    object_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing object name and the names of all of it's ancestors""")
    object_taxon: Optional[str] = Field(default=None)
    object_taxon_label: Optional[str] = Field(default=None)
    primary_knowledge_source: Optional[str] = Field(default=None)
    aggregator_knowledge_source: Optional[list[str]] = Field(default=None)
    negated: Optional[bool] = Field(default=None)
    pathway: Optional[str] = Field(default=None)
    evidence_count: Optional[int] = Field(default=None, description="""count of supporting documents, evidence codes, and sources supplying evidence""")
    knowledge_level: str = Field(default=..., description="""Describes the level of knowledge expressed in a statement, based on the reasoning or analysis methods used to generate the statement, or the scope or specificity of what the statement expresses to be true.""")
    agent_type: str = Field(default=..., description="""Describes the high-level category of agent who originally generated a  statement of knowledge or other type of information.""")
    has_evidence: Optional[list[str]] = Field(default=None)
    has_evidence_links: Optional[list[ExpandedCurie]] = Field(default=None, description="""List of ExpandedCuries with id and url for evidence""")
    has_count: Optional[int] = Field(default=None, description="""count of out of has_total representing a frequency""")
    has_total: Optional[int] = Field(default=None, description="""total, devided by has_count, representing a frequency""")
    has_percentage: Optional[float] = Field(default=None, description="""percentage, which may be calculated from has_count and has_total, as 100 * quotient or provided directly, rounded to the integer level""")
    has_quotient: Optional[float] = Field(default=None, description="""quotient, which should be 1/100 of has_percentage""")
    grouping_key: Optional[str] = Field(default=None, description="""A concatenation of fields used to group associations with the same essential/defining properties""")
    provided_by: Optional[str] = Field(default=None)
    provided_by_link: Optional[ExpandedCurie] = Field(default=None, description="""A link to the docs for the knowledge source that provided the node/edge.""")
    publications: Optional[list[str]] = Field(default=None)
    publications_links: Optional[list[ExpandedCurie]] = Field(default=None, description="""List of ExpandedCuries with id and url for publications""")
    frequency_qualifier: Optional[str] = Field(default=None)
    onset_qualifier: Optional[str] = Field(default=None)
    sex_qualifier: Optional[str] = Field(default=None)
    stage_qualifier: Optional[str] = Field(default=None)
    qualifiers: Optional[list[str]] = Field(default=None)
    qualifiers_label: Optional[str] = Field(default=None, description="""The name of the frequency_qualifier entity""")
    qualifiers_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the frequency_qualifier entity""")
    qualifiers_category: Optional[str] = Field(default=None, description="""The category of the frequency_qualifier entity""")
    qualifier: Optional[list[str]] = Field(default=None)
    qualifier_label: Optional[str] = Field(default=None, description="""The name of the frequency_qualifier entity""")
    qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the frequency_qualifier entity""")
    qualifier_category: Optional[str] = Field(default=None, description="""The category of the frequency_qualifier entity""")
    frequency_qualifier_label: Optional[str] = Field(default=None, description="""The name of the frequency_qualifier entity""")
    frequency_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the frequency_qualifier entity""")
    frequency_qualifier_category: Optional[str] = Field(default=None, description="""The category of the frequency_qualifier entity""")
    onset_qualifier_label: Optional[str] = Field(default=None, description="""The name of the onset_qualifier entity""")
    onset_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the onset_qualifier entity""")
    onset_qualifier_category: Optional[str] = Field(default=None, description="""The category of the onset_qualifier entity""")
    sex_qualifier_label: Optional[str] = Field(default=None, description="""The name of the sex_qualifier entity""")
    sex_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the sex_qualifier entity""")
    sex_qualifier_category: Optional[str] = Field(default=None, description="""The category of the sex_qualifier entity""")
    stage_qualifier_label: Optional[str] = Field(default=None, description="""The name of the stage_qualifier entity""")
    stage_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the stage_qualifier entity""")
    stage_qualifier_category: Optional[str] = Field(default=None, description="""The category of the stage_qualifier entity""")
    disease_context_qualifier: Optional[str] = Field(default=None, description="""A context qualifier representing a disease or condition in which a relationship expressed in an association took place.""")
    disease_context_qualifier_label: Optional[str] = Field(default=None, description="""The name of the disease_context_qualifier entity""")
    disease_context_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the disease_context_qualifier entity""")
    disease_context_qualifier_category: Optional[str] = Field(default=None, description="""The category of the disease_context_qualifier entity""")
    disease_context_qualifier_closure: Optional[list[str]] = Field(default=None, description="""Field containing disease_context_qualifier id and the ids of all of it's ancestors""")
    disease_context_qualifier_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing disease_context_qualifier name and the names of all of it's ancestors""")
    species_context_qualifier: Optional[str] = Field(default=None, description="""A context qualifier representing a species in which a relationship expressed in an association took place.""")
    species_context_qualifier_label: Optional[str] = Field(default=None, description="""The name of the species_context_qualifier entity""")
    species_context_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the species_context_qualifier entity""")
    species_context_qualifier_category: Optional[str] = Field(default=None, description="""The category of the species_context_qualifier entity""")
    subject_specialization_qualifier: Optional[str] = Field(default=None, description="""A qualifier that composes with a core subject/object concept to define a more specific version of the subject concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the subject identifier.""")
    subject_specialization_qualifier_label: Optional[str] = Field(default=None, description="""A label for the subject_specialization_qualifier""")
    subject_specialization_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the subject_specialization_qualifier""")
    subject_specialization_qualifier_category: Optional[str] = Field(default=None, description="""The category of the subject_specialization_qualifier""")
    subject_specialization_qualifier_closure: Optional[str] = Field(default=None, description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""")
    subject_specialization_qualifier_closure_label: Optional[str] = Field(default=None, description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""")
    object_specialization_qualifier: Optional[str] = Field(default=None, description="""A qualifier that composes with a core subject/object concept to define a more specific version of the object concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the object identifier.""")
    object_specialization_qualifier_label: Optional[str] = Field(default=None, description="""A label for the object_specialization_qualifier""")
    object_specialization_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the object_specialization_qualifier""")
    object_specialization_qualifier_category: Optional[str] = Field(default=None, description="""The category of the object_specialization_qualifier""")
    object_specialization_qualifier_closure: Optional[str] = Field(default=None, description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""")
    object_specialization_qualifier_closure_label: Optional[str] = Field(default=None, description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""")


class AssociationCountList(ConfiguredBaseModel):
    """
    Container class for a list of association counts
    """
    items: list[AssociationCount] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")


class CompactAssociation(ConfiguredBaseModel):
    category: Optional[str] = Field(default=None)
    subject: str = Field(default=...)
    subject_label: Optional[str] = Field(default=None, description="""The name of the subject entity""")
    predicate: str = Field(default=...)
    object: str = Field(default=...)
    object_label: Optional[str] = Field(default=None, description="""The name of the object entity""")
    negated: Optional[bool] = Field(default=None)


class AssociationTypeMapping(ConfiguredBaseModel):
    """
    A data class to hold the necessary information to produce association type counts for given  entities with appropriate directional labels
    """
    subject_label: Optional[str] = Field(default=None, description="""A label to describe the subjects of the association type as a whole for use in the UI""")
    object_label: Optional[str] = Field(default=None, description="""A label to describe the objects of the association type as a whole for use in the UI""")
    symmetric: bool = Field(default=False, description="""Whether the association type is symmetric, meaning that the subject and object labels should be interchangeable""")
    category: str = Field(default=..., description="""The biolink category to use in queries for this association type""")


class DirectionalAssociation(Association):
    """
    An association that gives it's direction relative to a specified entity
    """
    direction: AssociationDirectionEnum = Field(default=..., description="""The directionality of the association relative to a given entity for an association_count. If the entity is the subject or in the subject closure, the direction is forwards, if it is the object or in the object closure, the direction is backwards.""")
    highlighting: Optional[AssociationHighlighting] = Field(default=None, description="""Optional highlighting information for search results""")
    id: str = Field(default=...)
    category: Optional[str] = Field(default=None)
    subject: str = Field(default=...)
    original_subject: Optional[str] = Field(default=None)
    subject_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the subject entity""")
    subject_category: Optional[str] = Field(default=None, description="""The category of the subject entity""")
    subject_closure: Optional[list[str]] = Field(default=None, description="""Field containing subject id and the ids of all of it's ancestors""")
    subject_label: Optional[str] = Field(default=None, description="""The name of the subject entity""")
    subject_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing subject name and the names of all of it's ancestors""")
    subject_taxon: Optional[str] = Field(default=None)
    subject_taxon_label: Optional[str] = Field(default=None)
    predicate: str = Field(default=...)
    original_predicate: Optional[str] = Field(default=None, description="""used to hold the original relation/predicate that an external knowledge source uses before transformation to match the biolink-model specification.""")
    object: str = Field(default=...)
    original_object: Optional[str] = Field(default=None)
    object_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the object entity""")
    object_category: Optional[str] = Field(default=None, description="""The category of the object entity""")
    object_closure: Optional[list[str]] = Field(default=None, description="""Field containing object id and the ids of all of it's ancestors""")
    object_label: Optional[str] = Field(default=None, description="""The name of the object entity""")
    object_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing object name and the names of all of it's ancestors""")
    object_taxon: Optional[str] = Field(default=None)
    object_taxon_label: Optional[str] = Field(default=None)
    primary_knowledge_source: Optional[str] = Field(default=None)
    aggregator_knowledge_source: Optional[list[str]] = Field(default=None)
    negated: Optional[bool] = Field(default=None)
    pathway: Optional[str] = Field(default=None)
    evidence_count: Optional[int] = Field(default=None, description="""count of supporting documents, evidence codes, and sources supplying evidence""")
    knowledge_level: str = Field(default=..., description="""Describes the level of knowledge expressed in a statement, based on the reasoning or analysis methods used to generate the statement, or the scope or specificity of what the statement expresses to be true.""")
    agent_type: str = Field(default=..., description="""Describes the high-level category of agent who originally generated a  statement of knowledge or other type of information.""")
    has_evidence: Optional[list[str]] = Field(default=None)
    has_evidence_links: Optional[list[ExpandedCurie]] = Field(default=None, description="""List of ExpandedCuries with id and url for evidence""")
    has_count: Optional[int] = Field(default=None, description="""count of out of has_total representing a frequency""")
    has_total: Optional[int] = Field(default=None, description="""total, devided by has_count, representing a frequency""")
    has_percentage: Optional[float] = Field(default=None, description="""percentage, which may be calculated from has_count and has_total, as 100 * quotient or provided directly, rounded to the integer level""")
    has_quotient: Optional[float] = Field(default=None, description="""quotient, which should be 1/100 of has_percentage""")
    grouping_key: Optional[str] = Field(default=None, description="""A concatenation of fields used to group associations with the same essential/defining properties""")
    provided_by: Optional[str] = Field(default=None)
    provided_by_link: Optional[ExpandedCurie] = Field(default=None, description="""A link to the docs for the knowledge source that provided the node/edge.""")
    publications: Optional[list[str]] = Field(default=None)
    publications_links: Optional[list[ExpandedCurie]] = Field(default=None, description="""List of ExpandedCuries with id and url for publications""")
    frequency_qualifier: Optional[str] = Field(default=None)
    onset_qualifier: Optional[str] = Field(default=None)
    sex_qualifier: Optional[str] = Field(default=None)
    stage_qualifier: Optional[str] = Field(default=None)
    qualifiers: Optional[list[str]] = Field(default=None)
    qualifiers_label: Optional[str] = Field(default=None, description="""The name of the frequency_qualifier entity""")
    qualifiers_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the frequency_qualifier entity""")
    qualifiers_category: Optional[str] = Field(default=None, description="""The category of the frequency_qualifier entity""")
    qualifier: Optional[list[str]] = Field(default=None)
    qualifier_label: Optional[str] = Field(default=None, description="""The name of the frequency_qualifier entity""")
    qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the frequency_qualifier entity""")
    qualifier_category: Optional[str] = Field(default=None, description="""The category of the frequency_qualifier entity""")
    frequency_qualifier_label: Optional[str] = Field(default=None, description="""The name of the frequency_qualifier entity""")
    frequency_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the frequency_qualifier entity""")
    frequency_qualifier_category: Optional[str] = Field(default=None, description="""The category of the frequency_qualifier entity""")
    onset_qualifier_label: Optional[str] = Field(default=None, description="""The name of the onset_qualifier entity""")
    onset_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the onset_qualifier entity""")
    onset_qualifier_category: Optional[str] = Field(default=None, description="""The category of the onset_qualifier entity""")
    sex_qualifier_label: Optional[str] = Field(default=None, description="""The name of the sex_qualifier entity""")
    sex_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the sex_qualifier entity""")
    sex_qualifier_category: Optional[str] = Field(default=None, description="""The category of the sex_qualifier entity""")
    stage_qualifier_label: Optional[str] = Field(default=None, description="""The name of the stage_qualifier entity""")
    stage_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the stage_qualifier entity""")
    stage_qualifier_category: Optional[str] = Field(default=None, description="""The category of the stage_qualifier entity""")
    disease_context_qualifier: Optional[str] = Field(default=None, description="""A context qualifier representing a disease or condition in which a relationship expressed in an association took place.""")
    disease_context_qualifier_label: Optional[str] = Field(default=None, description="""The name of the disease_context_qualifier entity""")
    disease_context_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the disease_context_qualifier entity""")
    disease_context_qualifier_category: Optional[str] = Field(default=None, description="""The category of the disease_context_qualifier entity""")
    disease_context_qualifier_closure: Optional[list[str]] = Field(default=None, description="""Field containing disease_context_qualifier id and the ids of all of it's ancestors""")
    disease_context_qualifier_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing disease_context_qualifier name and the names of all of it's ancestors""")
    species_context_qualifier: Optional[str] = Field(default=None, description="""A context qualifier representing a species in which a relationship expressed in an association took place.""")
    species_context_qualifier_label: Optional[str] = Field(default=None, description="""The name of the species_context_qualifier entity""")
    species_context_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the species_context_qualifier entity""")
    species_context_qualifier_category: Optional[str] = Field(default=None, description="""The category of the species_context_qualifier entity""")
    subject_specialization_qualifier: Optional[str] = Field(default=None, description="""A qualifier that composes with a core subject/object concept to define a more specific version of the subject concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the subject identifier.""")
    subject_specialization_qualifier_label: Optional[str] = Field(default=None, description="""A label for the subject_specialization_qualifier""")
    subject_specialization_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the subject_specialization_qualifier""")
    subject_specialization_qualifier_category: Optional[str] = Field(default=None, description="""The category of the subject_specialization_qualifier""")
    subject_specialization_qualifier_closure: Optional[str] = Field(default=None, description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""")
    subject_specialization_qualifier_closure_label: Optional[str] = Field(default=None, description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""")
    object_specialization_qualifier: Optional[str] = Field(default=None, description="""A qualifier that composes with a core subject/object concept to define a more specific version of the object concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the object identifier.""")
    object_specialization_qualifier_label: Optional[str] = Field(default=None, description="""A label for the object_specialization_qualifier""")
    object_specialization_qualifier_namespace: Optional[str] = Field(default=None, description="""The namespace/prefix of the object_specialization_qualifier""")
    object_specialization_qualifier_category: Optional[str] = Field(default=None, description="""The category of the object_specialization_qualifier""")
    object_specialization_qualifier_closure: Optional[str] = Field(default=None, description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""")
    object_specialization_qualifier_closure_label: Optional[str] = Field(default=None, description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""")


class ExpandedCurie(ConfiguredBaseModel):
    """
    A curie bundled along with its expanded url
    """
    id: str = Field(default=...)
    url: Optional[str] = Field(default=None)


class Entity(ConfiguredBaseModel):
    """
    Represents an Entity in the Monarch KG data model
    """
    id: str = Field(default=...)
    category: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None, description="""The long form name of an entity""")
    deprecated: Optional[bool] = Field(default=None, description="""A boolean flag indicating that an entity is no longer considered current or valid.""")
    description: Optional[str] = Field(default=None)
    xref: Optional[list[str]] = Field(default=None)
    provided_by: Optional[str] = Field(default=None)
    in_taxon: Optional[str] = Field(default=None, description="""The biolink taxon that the entity is in the closure of.""")
    in_taxon_label: Optional[str] = Field(default=None, description="""The label of the biolink taxon that the entity is in the closure of.""")
    symbol: Optional[str] = Field(default=None)
    synonym: Optional[list[str]] = Field(default=None)
    broad_synonym: Optional[list[str]] = Field(default=None, description="""A broader synonym for the entity""")
    exact_synonym: Optional[list[str]] = Field(default=None, description="""An exact synonym for the entity""")
    narrow_synonym: Optional[list[str]] = Field(default=None, description="""A narrower synonym for the entity""")
    related_synonym: Optional[list[str]] = Field(default=None, description="""A related synonym for the entity""")
    subsets: Optional[list[str]] = Field(default=None, description="""A list of subsets that the entity belongs to""")
    uri: Optional[str] = Field(default=None, description="""The URI of the entity""")
    iri: Optional[str] = Field(default=None)
    namespace: Optional[str] = Field(default=None, description="""The namespace/prefix portion of this entity's identifier""")
    has_phenotype: Optional[list[str]] = Field(default=None, description="""A list of phenotype identifiers that are known to be associated with this entity""")
    has_phenotype_label: Optional[list[str]] = Field(default=None, description="""A list of phenotype labels that are known to be associated with this entity""")
    has_phenotype_closure: Optional[list[str]] = Field(default=None, description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""")
    has_phenotype_closure_label: Optional[list[str]] = Field(default=None, description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""")
    has_phenotype_count: Optional[int] = Field(default=None, description="""A count of the number of phenotypes that are known to be associated with this entity""")
    has_descendant: Optional[list[str]] = Field(default=None, description="""A list of entity identifiers that are known to be descendants of this entity""")
    has_descendant_label: Optional[list[str]] = Field(default=None, description="""A list of entity labels that are known to be descendants of this entity""")
    has_descendant_count: Optional[int] = Field(default=None, description="""A count of the number of entities that are known to be descendants of this entity""")


class FacetValue(ConfiguredBaseModel):
    label: str = Field(default=...)
    count: Optional[int] = Field(default=None, description="""count of documents""")


class AssociationCount(FacetValue):
    category: Optional[str] = Field(default=None)
    label: str = Field(default=...)
    count: Optional[int] = Field(default=None, description="""count of documents""")


class FacetField(ConfiguredBaseModel):
    label: str = Field(default=...)
    facet_values: Optional[list[FacetValue]] = Field(default=None, description="""Collection of FacetValue label/value instances belonging to a FacetField""")


class HistoPheno(ConfiguredBaseModel):
    id: str = Field(default=...)
    items: list[HistoBin] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")


class HistoBin(FacetValue):
    id: str = Field(default=...)
    label: str = Field(default=...)
    count: Optional[int] = Field(default=None, description="""count of documents""")


class Mapping(ConfiguredBaseModel):
    """
    A minimal class to hold a SSSOM mapping
    """
    subject_id: str = Field(default=...)
    subject_label: Optional[str] = Field(default=None, description="""The name of the subject entity""")
    predicate_id: str = Field(default=...)
    object_id: str = Field(default=...)
    object_label: Optional[str] = Field(default=None, description="""The name of the object entity""")
    mapping_justification: Optional[str] = Field(default=None)
    id: str = Field(default=...)


class Node(Entity):
    """
    UI container class extending Entity with additional information
    """
    in_taxon: Optional[str] = Field(default=None, description="""The biolink taxon that the entity is in the closure of.""")
    in_taxon_label: Optional[str] = Field(default=None, description="""The label of the biolink taxon that the entity is in the closure of.""")
    inheritance: Optional[Entity] = Field(default=None)
    causal_gene: Optional[list[Entity]] = Field(default=None, description="""A list of genes that are known to be causally associated with a disease""")
    causes_disease: Optional[list[Entity]] = Field(default=None, description="""A list of diseases that are known to be causally associated with a gene""")
    mappings: Optional[list[ExpandedCurie]] = Field(default=None, description="""List of ExpandedCuries with id and url for mapped entities""")
    external_links: Optional[list[ExpandedCurie]] = Field(default=None, description="""ExpandedCurie with id and url for xrefs""")
    provided_by_link: Optional[ExpandedCurie] = Field(default=None, description="""A link to the docs for the knowledge source that provided the node/edge.""")
    association_counts: list[AssociationCount] = Field(default=...)
    node_hierarchy: Optional[NodeHierarchy] = Field(default=None)
    id: str = Field(default=...)
    category: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None, description="""The long form name of an entity""")
    deprecated: Optional[bool] = Field(default=None, description="""A boolean flag indicating that an entity is no longer considered current or valid.""")
    description: Optional[str] = Field(default=None)
    xref: Optional[list[str]] = Field(default=None)
    provided_by: Optional[str] = Field(default=None)
    symbol: Optional[str] = Field(default=None)
    synonym: Optional[list[str]] = Field(default=None)
    broad_synonym: Optional[list[str]] = Field(default=None, description="""A broader synonym for the entity""")
    exact_synonym: Optional[list[str]] = Field(default=None, description="""An exact synonym for the entity""")
    narrow_synonym: Optional[list[str]] = Field(default=None, description="""A narrower synonym for the entity""")
    related_synonym: Optional[list[str]] = Field(default=None, description="""A related synonym for the entity""")
    subsets: Optional[list[str]] = Field(default=None, description="""A list of subsets that the entity belongs to""")
    uri: Optional[str] = Field(default=None, description="""The URI of the entity""")
    iri: Optional[str] = Field(default=None)
    namespace: Optional[str] = Field(default=None, description="""The namespace/prefix portion of this entity's identifier""")
    has_phenotype: Optional[list[str]] = Field(default=None, description="""A list of phenotype identifiers that are known to be associated with this entity""")
    has_phenotype_label: Optional[list[str]] = Field(default=None, description="""A list of phenotype labels that are known to be associated with this entity""")
    has_phenotype_closure: Optional[list[str]] = Field(default=None, description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""")
    has_phenotype_closure_label: Optional[list[str]] = Field(default=None, description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""")
    has_phenotype_count: Optional[int] = Field(default=None, description="""A count of the number of phenotypes that are known to be associated with this entity""")
    has_descendant: Optional[list[str]] = Field(default=None, description="""A list of entity identifiers that are known to be descendants of this entity""")
    has_descendant_label: Optional[list[str]] = Field(default=None, description="""A list of entity labels that are known to be descendants of this entity""")
    has_descendant_count: Optional[int] = Field(default=None, description="""A count of the number of entities that are known to be descendants of this entity""")


class NodeHierarchy(ConfiguredBaseModel):
    super_classes: list[Entity] = Field(default=...)
    sub_classes: list[Entity] = Field(default=...)


class Release(ConfiguredBaseModel):
    """
    A class to hold information about a release of the Monarch KG
    """
    version: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    kg: Optional[str] = Field(default=None)
    sqlite: Optional[str] = Field(default=None)
    solr: Optional[str] = Field(default=None)
    neo4j: Optional[str] = Field(default=None)
    metadata: Optional[str] = Field(default=None)
    graph_stats: Optional[str] = Field(default=None)
    qc_report: Optional[str] = Field(default=None)


class Results(ConfiguredBaseModel):
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class AssociationResults(Results):
    items: list[Association] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")
    facet_fields: Optional[list[FacetField]] = Field(default=None, description="""Collection of facet field responses with the field values and counts""")
    facet_queries: Optional[list[FacetValue]] = Field(default=None, description="""Collection of facet query responses with the query string values and counts""")
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class CompactAssociationResults(Results):
    items: list[CompactAssociation] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")
    facet_fields: Optional[list[FacetField]] = Field(default=None, description="""Collection of facet field responses with the field values and counts""")
    facet_queries: Optional[list[FacetValue]] = Field(default=None, description="""Collection of facet query responses with the query string values and counts""")
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class AssociationTableResults(Results):
    items: list[DirectionalAssociation] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")
    facet_fields: Optional[list[FacetField]] = Field(default=None, description="""Collection of facet field responses with the field values and counts""")
    facet_queries: Optional[list[FacetValue]] = Field(default=None, description="""Collection of facet query responses with the query string values and counts""")
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class CategoryGroupedAssociationResults(Results):
    counterpart_category: Optional[str] = Field(default=None, description="""The category of the counterpart entity in a given association,  eg. the category of the entity that is not the subject""")
    items: list[Association] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class EntityResults(Results):
    items: list[Entity] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class MappingResults(Results):
    """
    SSSOM Mappings returned as a results collection
    """
    items: list[Mapping] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class MultiEntityAssociationResults(Results):
    id: str = Field(default=...)
    name: Optional[str] = Field(default=None)
    associated_categories: list[CategoryGroupedAssociationResults] = Field(default=...)
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class SearchResult(Entity):
    score: Optional[float] = Field(default=None)
    id: str = Field(default=...)
    category: str = Field(default=...)
    name: str = Field(default=...)
    full_name: Optional[str] = Field(default=None, description="""The long form name of an entity""")
    deprecated: Optional[bool] = Field(default=None, description="""A boolean flag indicating that an entity is no longer considered current or valid.""")
    description: Optional[str] = Field(default=None)
    xref: Optional[list[str]] = Field(default=None)
    provided_by: Optional[str] = Field(default=None)
    in_taxon: Optional[str] = Field(default=None, description="""The biolink taxon that the entity is in the closure of.""")
    in_taxon_label: Optional[str] = Field(default=None, description="""The label of the biolink taxon that the entity is in the closure of.""")
    symbol: Optional[str] = Field(default=None)
    synonym: Optional[list[str]] = Field(default=None)
    broad_synonym: Optional[list[str]] = Field(default=None, description="""A broader synonym for the entity""")
    exact_synonym: Optional[list[str]] = Field(default=None, description="""An exact synonym for the entity""")
    narrow_synonym: Optional[list[str]] = Field(default=None, description="""A narrower synonym for the entity""")
    related_synonym: Optional[list[str]] = Field(default=None, description="""A related synonym for the entity""")
    subsets: Optional[list[str]] = Field(default=None, description="""A list of subsets that the entity belongs to""")
    uri: Optional[str] = Field(default=None, description="""The URI of the entity""")
    iri: Optional[str] = Field(default=None)
    namespace: Optional[str] = Field(default=None, description="""The namespace/prefix portion of this entity's identifier""")
    has_phenotype: Optional[list[str]] = Field(default=None, description="""A list of phenotype identifiers that are known to be associated with this entity""")
    has_phenotype_label: Optional[list[str]] = Field(default=None, description="""A list of phenotype labels that are known to be associated with this entity""")
    has_phenotype_closure: Optional[list[str]] = Field(default=None, description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""")
    has_phenotype_closure_label: Optional[list[str]] = Field(default=None, description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""")
    has_phenotype_count: Optional[int] = Field(default=None, description="""A count of the number of phenotypes that are known to be associated with this entity""")
    has_descendant: Optional[list[str]] = Field(default=None, description="""A list of entity identifiers that are known to be descendants of this entity""")
    has_descendant_label: Optional[list[str]] = Field(default=None, description="""A list of entity labels that are known to be descendants of this entity""")
    has_descendant_count: Optional[int] = Field(default=None, description="""A count of the number of entities that are known to be descendants of this entity""")


class SearchResults(Results):
    items: list[SearchResult] = Field(default=..., description="""A collection of items, with the type to be overriden by slot_usage""")
    facet_fields: Optional[list[FacetField]] = Field(default=None, description="""Collection of facet field responses with the field values and counts""")
    facet_queries: Optional[list[FacetValue]] = Field(default=None, description="""Collection of facet query responses with the query string values and counts""")
    limit: int = Field(default=..., description="""number of items to return in a response""")
    offset: int = Field(default=..., description="""offset into the total number of items""")
    total: int = Field(default=..., description="""total number of items matching a query""")


class TextAnnotationResult(ConfiguredBaseModel):
    text: Optional[str] = Field(default=None, description="""text without tokens""")
    tokens: Optional[list[Entity]] = Field(default=None, description="""A collection of entities or concepts""")
    start: Optional[int] = Field(default=None, description="""start position of the annotation""")
    end: Optional[int] = Field(default=None, description="""end position of the annotation""")


class AssociationHighlighting(ConfiguredBaseModel):
    """
    Optional highlighting information for search results
    """
    object_label: Optional[list[str]] = Field(default=None, description="""The name of the object entity""")
    object_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing object name and the names of all of it's ancestors""")
    subject_label: Optional[list[str]] = Field(default=None, description="""The name of the subject entity""")
    subject_closure_label: Optional[list[str]] = Field(default=None, description="""Field containing subject name and the names of all of it's ancestors""")
    predicate: Optional[list[str]] = Field(default=None)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
PairwiseSimilarity.model_rebuild()
TermPairwiseSimilarity.model_rebuild()
TermSetPairwiseSimilarity.model_rebuild()
TermInfo.model_rebuild()
BestMatch.model_rebuild()
SemsimSearchResult.model_rebuild()
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
AssociationHighlighting.model_rebuild()

