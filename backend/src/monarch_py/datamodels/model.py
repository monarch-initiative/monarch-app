from __future__ import annotations
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    pass


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta(
    {
        "default_prefix": "https://w3id.org/monarch/monarch-py/",
        "default_range": "string",
        "description": "Data models for the Monarch Initiative data access library",
        "id": "https://w3id.org/monarch/monarch-py",
        "imports": ["linkml:types", "similarity"],
        "name": "monarch-py",
        "prefixes": {
            "biolink": {"prefix_prefix": "biolink", "prefix_reference": "https://w3id.org/biolink/vocab/"},
            "linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"},
        },
        "source_file": "/Users/kschaper/Monarch/monarch-app/backend/src/monarch_py/datamodels/model.yaml",
    }
)


class AssociationDirectionEnum(str, Enum):
    """
    The directionality of an association as it relates to a specified entity, with edges being categorized as incoming or outgoing
    """

    # An association for which a specified entity is the object or part of the object closure
    incoming = "incoming"
    # An association for which a specified entity is the subject or part of the subject closure
    outgoing = "outgoing"


class PairwiseSimilarity(ConfiguredBaseModel):
    """
    Abstract grouping for representing individual pairwise similarities
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"abstract": True, "from_schema": "https://w3id.org/monarch/monarch-py-similarity"}
    )

    pass


class TermPairwiseSimilarity(PairwiseSimilarity):
    """
    A simple pairwise similarity between two atomic concepts/terms
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py-similarity"})

    subject_id: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "subject_id", "domain_of": ["TermPairwiseSimilarity", "Mapping"]}},
    )
    subject_label: Optional[str] = Field(
        None,
        description="""The name of the subject entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    subject_source: Optional[str] = Field(
        None,
        description="""the source for the first entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_source",
                "domain_of": ["TermPairwiseSimilarity"],
                "slot_uri": "sssom:subject_source",
            }
        },
    )
    object_id: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "object_id", "domain_of": ["TermPairwiseSimilarity", "Mapping"]}},
    )
    object_label: Optional[str] = Field(
        None,
        description="""The name of the object entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    object_source: Optional[str] = Field(
        None,
        description="""the source for the second entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_source",
                "domain_of": ["TermPairwiseSimilarity"],
                "slot_uri": "sssom:object_source",
            }
        },
    )
    ancestor_id: Optional[str] = Field(
        None,
        description="""the most recent common ancestor of the two compared entities. If there are multiple MRCAs then the most informative one is selected""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "ancestor_id",
                "domain_of": ["TermPairwiseSimilarity"],
                "todos": ["decide on what to do when there are multiple possible ancestos"],
            }
        },
    )
    ancestor_label: Optional[str] = Field(
        None,
        description="""the name or label of the ancestor concept""",
        json_schema_extra={"linkml_meta": {"alias": "ancestor_label", "domain_of": ["TermPairwiseSimilarity"]}},
    )
    ancestor_source: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "ancestor_source", "domain_of": ["TermPairwiseSimilarity"]}}
    )
    object_information_content: Optional[float] = Field(
        None,
        description="""The IC of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_information_content",
                "domain_of": ["TermPairwiseSimilarity"],
                "is_a": "information_content",
            }
        },
    )
    subject_information_content: Optional[float] = Field(
        None,
        description="""The IC of the subject""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_information_content",
                "domain_of": ["TermPairwiseSimilarity"],
                "is_a": "information_content",
            }
        },
    )
    ancestor_information_content: Optional[float] = Field(
        None,
        description="""The IC of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "ancestor_information_content",
                "domain_of": ["TermPairwiseSimilarity"],
                "is_a": "information_content",
            }
        },
    )
    jaccard_similarity: Optional[float] = Field(
        None,
        description="""The number of concepts in the intersection divided by the number in the union""",
        json_schema_extra={
            "linkml_meta": {"alias": "jaccard_similarity", "domain_of": ["TermPairwiseSimilarity"], "is_a": "score"}
        },
    )
    cosine_similarity: Optional[float] = Field(
        None,
        description="""the dot product of two node embeddings divided by the product of their lengths""",
        json_schema_extra={
            "linkml_meta": {"alias": "cosine_similarity", "domain_of": ["TermPairwiseSimilarity"], "is_a": "score"}
        },
    )
    dice_similarity: Optional[float] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "dice_similarity", "domain_of": ["TermPairwiseSimilarity"], "is_a": "score"}
        },
    )
    phenodigm_score: Optional[float] = Field(
        None,
        description="""the geometric mean of the jaccard similarity and the information content""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "phenodigm_score",
                "domain_of": ["TermPairwiseSimilarity"],
                "equals_expression": "sqrt({jaccard_similarity} * {information_content})",
                "is_a": "score",
            }
        },
    )


class TermSetPairwiseSimilarity(PairwiseSimilarity):
    """
    A simple pairwise similarity between two sets of concepts/terms
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py-similarity"})

    subject_termset: Optional[Dict[str, Union[str, TermInfo]]] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "subject_termset", "domain_of": ["TermSetPairwiseSimilarity"]}},
    )
    object_termset: Optional[Dict[str, Union[str, TermInfo]]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "object_termset", "domain_of": ["TermSetPairwiseSimilarity"]}}
    )
    subject_best_matches: Optional[Dict[str, BestMatch]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "subject_best_matches", "domain_of": ["TermSetPairwiseSimilarity"]}
        },
    )
    object_best_matches: Optional[Dict[str, BestMatch]] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "object_best_matches", "domain_of": ["TermSetPairwiseSimilarity"]}},
    )
    average_score: Optional[float] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "average_score", "domain_of": ["TermSetPairwiseSimilarity"]}}
    )
    best_score: Optional[float] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "best_score", "domain_of": ["TermSetPairwiseSimilarity"]}}
    )
    metric: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "metric", "domain_of": ["TermSetPairwiseSimilarity"]}}
    )


class TermInfo(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py-similarity"})

    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    label: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": ["TermInfo", "FacetValue", "FacetField"],
                "slot_uri": "rdfs:label",
            }
        },
    )


class BestMatch(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py-similarity"})

    match_source: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "match_source",
                "comments": ["note that the match_source is either the subject or the object"],
                "domain_of": ["BestMatch"],
            }
        },
    )
    match_source_label: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "match_source_label", "domain_of": ["BestMatch"]}}
    )
    match_target: Optional[str] = Field(
        None,
        description="""the entity matches""",
        json_schema_extra={"linkml_meta": {"alias": "match_target", "domain_of": ["BestMatch"]}},
    )
    match_target_label: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "match_target_label", "domain_of": ["BestMatch"]}}
    )
    score: float = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {"alias": "score", "domain_of": ["BestMatch", "SemsimSearchResult", "SearchResult"]}
        },
    )
    match_subsumer: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "match_subsumer", "domain_of": ["BestMatch"]}}
    )
    match_subsumer_label: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "match_subsumer_label", "domain_of": ["BestMatch"]}}
    )
    similarity: TermPairwiseSimilarity = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "similarity", "domain_of": ["BestMatch", "SemsimSearchResult"]}},
    )


class SemsimSearchResult(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py-similarity",
            "slot_usage": {"subject": {"inlined": True, "name": "subject", "range": "Entity"}},
        }
    )

    subject: Entity = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject",
                "domain_of": ["SemsimSearchResult", "Association", "CompactAssociation"],
            }
        },
    )
    score: Optional[float] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "score", "domain_of": ["BestMatch", "SemsimSearchResult", "SearchResult"]}
        },
    )
    similarity: Optional[TermSetPairwiseSimilarity] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "similarity", "domain_of": ["BestMatch", "SemsimSearchResult"]}},
    )


class Association(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    category: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )
    subject: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject",
                "domain_of": ["SemsimSearchResult", "Association", "CompactAssociation"],
            }
        },
    )
    original_subject: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "original_subject", "domain_of": ["Association"]}}
    )
    subject_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the subject entity""",
        json_schema_extra={"linkml_meta": {"alias": "subject_namespace", "domain_of": ["Association"]}},
    )
    subject_category: Optional[str] = Field(
        None,
        description="""The category of the subject entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    subject_closure: Optional[List[str]] = Field(
        None,
        description="""Field containing subject id and the ids of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "subject_closure", "domain_of": ["Association"]}},
    )
    subject_label: Optional[str] = Field(
        None,
        description="""The name of the subject entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    subject_closure_label: Optional[List[str]] = Field(
        None,
        description="""Field containing subject name and the names of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "subject_closure_label", "domain_of": ["Association"]}},
    )
    subject_taxon: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "subject_taxon", "domain_of": ["Association"], "is_a": "in_taxon"}},
    )
    subject_taxon_label: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "subject_taxon_label", "domain_of": ["Association"], "is_a": "in_taxon_label"}
        },
    )
    predicate: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "predicate", "domain_of": ["Association", "CompactAssociation"]}},
    )
    original_predicate: Optional[str] = Field(
        None,
        description="""used to hold the original relation/predicate that an external knowledge source uses before transformation to match the biolink-model specification.""",
        json_schema_extra={"linkml_meta": {"alias": "original_predicate", "domain_of": ["Association"]}},
    )
    object: str = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "object", "domain_of": ["Association", "CompactAssociation"]}}
    )
    original_object: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "original_object", "domain_of": ["Association"]}}
    )
    object_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the object entity""",
        json_schema_extra={"linkml_meta": {"alias": "object_namespace", "domain_of": ["Association"]}},
    )
    object_category: Optional[str] = Field(
        None,
        description="""The category of the object entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    object_closure: Optional[List[str]] = Field(
        None,
        description="""Field containing object id and the ids of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "object_closure", "domain_of": ["Association"]}},
    )
    object_label: Optional[str] = Field(
        None,
        description="""The name of the object entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    object_closure_label: Optional[List[str]] = Field(
        None,
        description="""Field containing object name and the names of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "object_closure_label", "domain_of": ["Association"]}},
    )
    object_taxon: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "object_taxon", "domain_of": ["Association"], "is_a": "in_taxon"}},
    )
    object_taxon_label: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "object_taxon_label", "domain_of": ["Association"], "is_a": "in_taxon_label"}
        },
    )
    primary_knowledge_source: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "primary_knowledge_source", "domain_of": ["Association"]}}
    )
    aggregator_knowledge_source: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "aggregator_knowledge_source", "domain_of": ["Association"]}}
    )
    negated: Optional[bool] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "negated", "domain_of": ["Association", "CompactAssociation"]}},
    )
    pathway: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "pathway", "domain_of": ["Association"]}}
    )
    evidence_count: Optional[int] = Field(
        None,
        description="""count of supporting documents, evidence codes, and sources supplying evidence""",
        json_schema_extra={"linkml_meta": {"alias": "evidence_count", "domain_of": ["Association"]}},
    )
    knowledge_level: str = Field(
        ...,
        description="""Describes the level of knowledge expressed in a statement, based on the reasoning or analysis methods used to generate the statement, or the scope or specificity of what the statement expresses to be true.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "knowledge_level",
                "domain_of": ["Association"],
                "notes": [
                    "The range in this schema is represented as a string, but is "
                    "constrained  to values from biolink:KnowledgeLevelEnum at ingest "
                    "time"
                ],
                "slot_uri": "biolink:knowledge_level",
            }
        },
    )
    agent_type: str = Field(
        ...,
        description="""Describes the high-level category of agent who originally generated a  statement of knowledge or other type of information.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "agent_type",
                "domain_of": ["Association"],
                "notes": [
                    "The range in this schema is represented as a string, but is "
                    "constrained  to values from biolink:AgentTypeEnum at ingest time"
                ],
                "slot_uri": "biolink:agent_type",
            }
        },
    )
    has_evidence: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "has_evidence", "domain_of": ["Association"]}}
    )
    has_evidence_links: Optional[List[ExpandedCurie]] = Field(
        None,
        description="""List of ExpandedCuries with id and url for evidence""",
        json_schema_extra={"linkml_meta": {"alias": "has_evidence_links", "domain_of": ["Association"]}},
    )
    has_count: Optional[int] = Field(
        None,
        description="""count of out of has_total representing a frequency""",
        json_schema_extra={"linkml_meta": {"alias": "has_count", "domain_of": ["Association"]}},
    )
    has_total: Optional[int] = Field(
        None,
        description="""total, devided by has_count, representing a frequency""",
        json_schema_extra={"linkml_meta": {"alias": "has_total", "domain_of": ["Association"]}},
    )
    has_percentage: Optional[float] = Field(
        None,
        description="""percentage, which may be calculated from has_count and has_total, as 100 * quotient or provided directly, rounded to the integer level""",
        json_schema_extra={"linkml_meta": {"alias": "has_percentage", "domain_of": ["Association"]}},
    )
    has_quotient: Optional[float] = Field(
        None,
        description="""quotient, which should be 1/100 of has_percentage""",
        json_schema_extra={"linkml_meta": {"alias": "has_quotient", "domain_of": ["Association"]}},
    )
    grouping_key: Optional[str] = Field(
        None,
        description="""A concatenation of fields used to group associations with the same essential/defining properties""",
        json_schema_extra={"linkml_meta": {"alias": "grouping_key", "domain_of": ["Association"]}},
    )
    provided_by: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "provided_by", "domain_of": ["Association", "Entity"]}}
    )
    provided_by_link: Optional[ExpandedCurie] = Field(
        None,
        description="""A link to the docs for the knowledge source that provided the node/edge.""",
        json_schema_extra={"linkml_meta": {"alias": "provided_by_link", "domain_of": ["Association", "Node"]}},
    )
    publications: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "publications", "domain_of": ["Association"]}}
    )
    publications_links: Optional[List[ExpandedCurie]] = Field(
        None,
        description="""List of ExpandedCuries with id and url for publications""",
        json_schema_extra={"linkml_meta": {"alias": "publications_links", "domain_of": ["Association"]}},
    )
    frequency_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "frequency_qualifier", "domain_of": ["Association"]}}
    )
    onset_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "onset_qualifier", "domain_of": ["Association"]}}
    )
    sex_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "sex_qualifier", "domain_of": ["Association"]}}
    )
    stage_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "stage_qualifier", "domain_of": ["Association"]}}
    )
    qualifiers: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "qualifiers", "domain_of": ["Association"]}}
    )
    qualifiers_label: Optional[str] = Field(
        None,
        description="""The name of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifiers_label", "domain_of": ["Association"], "is_a": "name"}},
    )
    qualifiers_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifiers_namespace", "domain_of": ["Association"]}},
    )
    qualifiers_category: Optional[str] = Field(
        None,
        description="""The category of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "qualifiers_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    qualifier: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "qualifier", "domain_of": ["Association"]}}
    )
    qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifier_label", "domain_of": ["Association"], "is_a": "name"}},
    )
    qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifier_namespace", "domain_of": ["Association"]}},
    )
    qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    frequency_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "frequency_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    frequency_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "frequency_qualifier_namespace", "domain_of": ["Association"]}},
    )
    frequency_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "frequency_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    onset_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the onset_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "onset_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    onset_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the onset_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "onset_qualifier_namespace", "domain_of": ["Association"]}},
    )
    onset_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the onset_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "onset_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    sex_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the sex_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "sex_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    sex_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the sex_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "sex_qualifier_namespace", "domain_of": ["Association"]}},
    )
    sex_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the sex_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "sex_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    stage_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the stage_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "stage_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    stage_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the stage_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "stage_qualifier_namespace", "domain_of": ["Association"]}},
    )
    stage_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the stage_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "stage_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    disease_context_qualifier: Optional[str] = Field(
        None,
        description="""A context qualifier representing a disease or condition in which a relationship expressed in an association took place.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "disease_context_qualifier",
                "domain_of": ["Association"],
                "examples": [{"value": "MONDO:0004979"}, {"value": "MONDO:0005148"}],
            }
        },
    )
    disease_context_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the disease_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "disease_context_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    disease_context_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the disease_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "disease_context_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    disease_context_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the disease_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "disease_context_qualifier_category",
                "domain_of": ["Association"],
                "is_a": "category",
            }
        },
    )
    disease_context_qualifier_closure: Optional[List[str]] = Field(
        None,
        description="""Field containing disease_context_qualifier id and the ids of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "disease_context_qualifier_closure", "domain_of": ["Association"]}},
    )
    disease_context_qualifier_closure_label: Optional[List[str]] = Field(
        None,
        description="""Field containing disease_context_qualifier name and the names of all of it's ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "disease_context_qualifier_closure_label", "domain_of": ["Association"]}
        },
    )
    species_context_qualifier: Optional[str] = Field(
        None,
        description="""A context qualifier representing a species in which a relationship expressed in an association took place.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "species_context_qualifier",
                "domain_of": ["Association"],
                "examples": [{"value": "NCBITaxon:9606"}],
            }
        },
    )
    species_context_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the species_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "species_context_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    species_context_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the species_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "species_context_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    species_context_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the species_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "species_context_qualifier_category",
                "domain_of": ["Association"],
                "is_a": "category",
            }
        },
    )
    subject_specialization_qualifier: Optional[str] = Field(
        None,
        description="""A qualifier that composes with a core subject/object concept to define a more specific version of the subject concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the subject identifier.""",
        json_schema_extra={"linkml_meta": {"alias": "subject_specialization_qualifier", "domain_of": ["Association"]}},
    )
    subject_specialization_qualifier_label: Optional[str] = Field(
        None,
        description="""A label for the subject_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_label", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the subject_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the subject_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_category", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_closure: Optional[str] = Field(
        None,
        description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_closure", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_closure_label: Optional[str] = Field(
        None,
        description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_closure_label", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier: Optional[str] = Field(
        None,
        description="""A qualifier that composes with a core subject/object concept to define a more specific version of the object concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the object identifier.""",
        json_schema_extra={"linkml_meta": {"alias": "object_specialization_qualifier", "domain_of": ["Association"]}},
    )
    object_specialization_qualifier_label: Optional[str] = Field(
        None,
        description="""A label for the object_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_label", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the object_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the object_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_category", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_closure: Optional[str] = Field(
        None,
        description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_closure", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_closure_label: Optional[str] = Field(
        None,
        description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_closure_label", "domain_of": ["Association"]}
        },
    )


class AssociationCountList(ConfiguredBaseModel):
    """
    Container class for a list of association counts
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "AssociationCount"}},
        }
    )

    items: List[AssociationCount] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )


class CompactAssociation(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    category: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )
    subject: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject",
                "domain_of": ["SemsimSearchResult", "Association", "CompactAssociation"],
            }
        },
    )
    subject_label: Optional[str] = Field(
        None,
        description="""The name of the subject entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    predicate: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "predicate", "domain_of": ["Association", "CompactAssociation"]}},
    )
    object: str = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "object", "domain_of": ["Association", "CompactAssociation"]}}
    )
    object_label: Optional[str] = Field(
        None,
        description="""The name of the object entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    negated: Optional[bool] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "negated", "domain_of": ["Association", "CompactAssociation"]}},
    )


class AssociationTypeMapping(ConfiguredBaseModel):
    """
    A data class to hold the necessary information to produce association type counts for given  entities with appropriate directional labels
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {
                "category": {
                    "description": "The biolink category to use in " "queries for this association type",
                    "multivalued": False,
                    "name": "category",
                    "required": True,
                },
                "object_label": {
                    "description": "A label to describe the "
                    "objects of the association "
                    "type as a whole for use in "
                    "the UI",
                    "name": "object_label",
                },
                "subject_label": {
                    "description": "A label to describe the "
                    "subjects of the association "
                    "type as a whole for use in "
                    "the UI",
                    "name": "subject_label",
                },
                "symmetric": {
                    "description": "Whether the association type is "
                    "symmetric, meaning that the "
                    "subject and object labels should "
                    "be interchangeable",
                    "ifabsent": "False",
                    "name": "symmetric",
                    "required": True,
                },
            },
        }
    )

    subject_label: Optional[str] = Field(
        None,
        description="""A label to describe the subjects of the association type as a whole for use in the UI""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    object_label: Optional[str] = Field(
        None,
        description="""A label to describe the objects of the association type as a whole for use in the UI""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    symmetric: bool = Field(
        False,
        description="""Whether the association type is symmetric, meaning that the subject and object labels should be interchangeable""",
        json_schema_extra={
            "linkml_meta": {"alias": "symmetric", "domain_of": ["AssociationTypeMapping"], "ifabsent": "False"}
        },
    )
    category: str = Field(
        ...,
        description="""The biolink category to use in queries for this association type""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )


class DirectionalAssociation(Association):
    """
    An association that gives it's direction relative to a specified entity
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    direction: AssociationDirectionEnum = Field(
        ...,
        description="""The directionality of the association relative to a given entity for an association_count. If the entity is the subject or in the subject closure, the direction is forwards, if it is the object or in the object closure, the direction is backwards.""",
        json_schema_extra={"linkml_meta": {"alias": "direction", "domain_of": ["DirectionalAssociation"]}},
    )
    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    category: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )
    subject: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject",
                "domain_of": ["SemsimSearchResult", "Association", "CompactAssociation"],
            }
        },
    )
    original_subject: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "original_subject", "domain_of": ["Association"]}}
    )
    subject_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the subject entity""",
        json_schema_extra={"linkml_meta": {"alias": "subject_namespace", "domain_of": ["Association"]}},
    )
    subject_category: Optional[str] = Field(
        None,
        description="""The category of the subject entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    subject_closure: Optional[List[str]] = Field(
        None,
        description="""Field containing subject id and the ids of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "subject_closure", "domain_of": ["Association"]}},
    )
    subject_label: Optional[str] = Field(
        None,
        description="""The name of the subject entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    subject_closure_label: Optional[List[str]] = Field(
        None,
        description="""Field containing subject name and the names of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "subject_closure_label", "domain_of": ["Association"]}},
    )
    subject_taxon: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "subject_taxon", "domain_of": ["Association"], "is_a": "in_taxon"}},
    )
    subject_taxon_label: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "subject_taxon_label", "domain_of": ["Association"], "is_a": "in_taxon_label"}
        },
    )
    predicate: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "predicate", "domain_of": ["Association", "CompactAssociation"]}},
    )
    original_predicate: Optional[str] = Field(
        None,
        description="""used to hold the original relation/predicate that an external knowledge source uses before transformation to match the biolink-model specification.""",
        json_schema_extra={"linkml_meta": {"alias": "original_predicate", "domain_of": ["Association"]}},
    )
    object: str = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "object", "domain_of": ["Association", "CompactAssociation"]}}
    )
    original_object: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "original_object", "domain_of": ["Association"]}}
    )
    object_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the object entity""",
        json_schema_extra={"linkml_meta": {"alias": "object_namespace", "domain_of": ["Association"]}},
    )
    object_category: Optional[str] = Field(
        None,
        description="""The category of the object entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    object_closure: Optional[List[str]] = Field(
        None,
        description="""Field containing object id and the ids of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "object_closure", "domain_of": ["Association"]}},
    )
    object_label: Optional[str] = Field(
        None,
        description="""The name of the object entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    object_closure_label: Optional[List[str]] = Field(
        None,
        description="""Field containing object name and the names of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "object_closure_label", "domain_of": ["Association"]}},
    )
    object_taxon: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "object_taxon", "domain_of": ["Association"], "is_a": "in_taxon"}},
    )
    object_taxon_label: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "object_taxon_label", "domain_of": ["Association"], "is_a": "in_taxon_label"}
        },
    )
    primary_knowledge_source: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "primary_knowledge_source", "domain_of": ["Association"]}}
    )
    aggregator_knowledge_source: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "aggregator_knowledge_source", "domain_of": ["Association"]}}
    )
    negated: Optional[bool] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "negated", "domain_of": ["Association", "CompactAssociation"]}},
    )
    pathway: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "pathway", "domain_of": ["Association"]}}
    )
    evidence_count: Optional[int] = Field(
        None,
        description="""count of supporting documents, evidence codes, and sources supplying evidence""",
        json_schema_extra={"linkml_meta": {"alias": "evidence_count", "domain_of": ["Association"]}},
    )
    knowledge_level: str = Field(
        ...,
        description="""Describes the level of knowledge expressed in a statement, based on the reasoning or analysis methods used to generate the statement, or the scope or specificity of what the statement expresses to be true.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "knowledge_level",
                "domain_of": ["Association"],
                "notes": [
                    "The range in this schema is represented as a string, but is "
                    "constrained  to values from biolink:KnowledgeLevelEnum at ingest "
                    "time"
                ],
                "slot_uri": "biolink:knowledge_level",
            }
        },
    )
    agent_type: str = Field(
        ...,
        description="""Describes the high-level category of agent who originally generated a  statement of knowledge or other type of information.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "agent_type",
                "domain_of": ["Association"],
                "notes": [
                    "The range in this schema is represented as a string, but is "
                    "constrained  to values from biolink:AgentTypeEnum at ingest time"
                ],
                "slot_uri": "biolink:agent_type",
            }
        },
    )
    has_evidence: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "has_evidence", "domain_of": ["Association"]}}
    )
    has_evidence_links: Optional[List[ExpandedCurie]] = Field(
        None,
        description="""List of ExpandedCuries with id and url for evidence""",
        json_schema_extra={"linkml_meta": {"alias": "has_evidence_links", "domain_of": ["Association"]}},
    )
    has_count: Optional[int] = Field(
        None,
        description="""count of out of has_total representing a frequency""",
        json_schema_extra={"linkml_meta": {"alias": "has_count", "domain_of": ["Association"]}},
    )
    has_total: Optional[int] = Field(
        None,
        description="""total, devided by has_count, representing a frequency""",
        json_schema_extra={"linkml_meta": {"alias": "has_total", "domain_of": ["Association"]}},
    )
    has_percentage: Optional[float] = Field(
        None,
        description="""percentage, which may be calculated from has_count and has_total, as 100 * quotient or provided directly, rounded to the integer level""",
        json_schema_extra={"linkml_meta": {"alias": "has_percentage", "domain_of": ["Association"]}},
    )
    has_quotient: Optional[float] = Field(
        None,
        description="""quotient, which should be 1/100 of has_percentage""",
        json_schema_extra={"linkml_meta": {"alias": "has_quotient", "domain_of": ["Association"]}},
    )
    grouping_key: Optional[str] = Field(
        None,
        description="""A concatenation of fields used to group associations with the same essential/defining properties""",
        json_schema_extra={"linkml_meta": {"alias": "grouping_key", "domain_of": ["Association"]}},
    )
    provided_by: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "provided_by", "domain_of": ["Association", "Entity"]}}
    )
    provided_by_link: Optional[ExpandedCurie] = Field(
        None,
        description="""A link to the docs for the knowledge source that provided the node/edge.""",
        json_schema_extra={"linkml_meta": {"alias": "provided_by_link", "domain_of": ["Association", "Node"]}},
    )
    publications: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "publications", "domain_of": ["Association"]}}
    )
    publications_links: Optional[List[ExpandedCurie]] = Field(
        None,
        description="""List of ExpandedCuries with id and url for publications""",
        json_schema_extra={"linkml_meta": {"alias": "publications_links", "domain_of": ["Association"]}},
    )
    frequency_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "frequency_qualifier", "domain_of": ["Association"]}}
    )
    onset_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "onset_qualifier", "domain_of": ["Association"]}}
    )
    sex_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "sex_qualifier", "domain_of": ["Association"]}}
    )
    stage_qualifier: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "stage_qualifier", "domain_of": ["Association"]}}
    )
    qualifiers: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "qualifiers", "domain_of": ["Association"]}}
    )
    qualifiers_label: Optional[str] = Field(
        None,
        description="""The name of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifiers_label", "domain_of": ["Association"], "is_a": "name"}},
    )
    qualifiers_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifiers_namespace", "domain_of": ["Association"]}},
    )
    qualifiers_category: Optional[str] = Field(
        None,
        description="""The category of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "qualifiers_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    qualifier: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "qualifier", "domain_of": ["Association"]}}
    )
    qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifier_label", "domain_of": ["Association"], "is_a": "name"}},
    )
    qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "qualifier_namespace", "domain_of": ["Association"]}},
    )
    qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    frequency_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "frequency_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    frequency_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the frequency_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "frequency_qualifier_namespace", "domain_of": ["Association"]}},
    )
    frequency_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the frequency_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "frequency_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    onset_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the onset_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "onset_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    onset_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the onset_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "onset_qualifier_namespace", "domain_of": ["Association"]}},
    )
    onset_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the onset_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "onset_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    sex_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the sex_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "sex_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    sex_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the sex_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "sex_qualifier_namespace", "domain_of": ["Association"]}},
    )
    sex_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the sex_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "sex_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    stage_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the stage_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "stage_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    stage_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the stage_qualifier entity""",
        json_schema_extra={"linkml_meta": {"alias": "stage_qualifier_namespace", "domain_of": ["Association"]}},
    )
    stage_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the stage_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "stage_qualifier_category", "domain_of": ["Association"], "is_a": "category"}
        },
    )
    disease_context_qualifier: Optional[str] = Field(
        None,
        description="""A context qualifier representing a disease or condition in which a relationship expressed in an association took place.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "disease_context_qualifier",
                "domain_of": ["Association"],
                "examples": [{"value": "MONDO:0004979"}, {"value": "MONDO:0005148"}],
            }
        },
    )
    disease_context_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the disease_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "disease_context_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    disease_context_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the disease_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "disease_context_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    disease_context_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the disease_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "disease_context_qualifier_category",
                "domain_of": ["Association"],
                "is_a": "category",
            }
        },
    )
    disease_context_qualifier_closure: Optional[List[str]] = Field(
        None,
        description="""Field containing disease_context_qualifier id and the ids of all of it's ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "disease_context_qualifier_closure", "domain_of": ["Association"]}},
    )
    disease_context_qualifier_closure_label: Optional[List[str]] = Field(
        None,
        description="""Field containing disease_context_qualifier name and the names of all of it's ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "disease_context_qualifier_closure_label", "domain_of": ["Association"]}
        },
    )
    species_context_qualifier: Optional[str] = Field(
        None,
        description="""A context qualifier representing a species in which a relationship expressed in an association took place.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "species_context_qualifier",
                "domain_of": ["Association"],
                "examples": [{"value": "NCBITaxon:9606"}],
            }
        },
    )
    species_context_qualifier_label: Optional[str] = Field(
        None,
        description="""The name of the species_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "species_context_qualifier_label", "domain_of": ["Association"], "is_a": "name"}
        },
    )
    species_context_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the species_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {"alias": "species_context_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    species_context_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the species_context_qualifier entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "species_context_qualifier_category",
                "domain_of": ["Association"],
                "is_a": "category",
            }
        },
    )
    subject_specialization_qualifier: Optional[str] = Field(
        None,
        description="""A qualifier that composes with a core subject/object concept to define a more specific version of the subject concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the subject identifier.""",
        json_schema_extra={"linkml_meta": {"alias": "subject_specialization_qualifier", "domain_of": ["Association"]}},
    )
    subject_specialization_qualifier_label: Optional[str] = Field(
        None,
        description="""A label for the subject_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_label", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the subject_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the subject_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_category", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_closure: Optional[str] = Field(
        None,
        description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_closure", "domain_of": ["Association"]}
        },
    )
    subject_specialization_qualifier_closure_label: Optional[str] = Field(
        None,
        description="""A closure of the subject_specialization_qualifier, including the subject_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "subject_specialization_qualifier_closure_label", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier: Optional[str] = Field(
        None,
        description="""A qualifier that composes with a core subject/object concept to define a more specific version of the object concept, specifically using an ontology term that is not a subclass or descendant of the core concept and in the vast majority of cases, is of a different ontological namespace than the category or namespace of the object identifier.""",
        json_schema_extra={"linkml_meta": {"alias": "object_specialization_qualifier", "domain_of": ["Association"]}},
    )
    object_specialization_qualifier_label: Optional[str] = Field(
        None,
        description="""A label for the object_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_label", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix of the object_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_namespace", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_category: Optional[str] = Field(
        None,
        description="""The category of the object_specialization_qualifier""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_category", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_closure: Optional[str] = Field(
        None,
        description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_closure", "domain_of": ["Association"]}
        },
    )
    object_specialization_qualifier_closure_label: Optional[str] = Field(
        None,
        description="""A closure of the object_specialization_qualifier, including the object_specialization_qualifier itself and all of its ancestors""",
        json_schema_extra={
            "linkml_meta": {"alias": "object_specialization_qualifier_closure_label", "domain_of": ["Association"]}
        },
    )


class ExpandedCurie(ConfiguredBaseModel):
    """
    A curie bundled along with its expanded url
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    url: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "url", "domain_of": ["ExpandedCurie", "Release"]}}
    )


class Entity(ConfiguredBaseModel):
    """
    Represents an Entity in the Monarch KG data model
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    category: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )
    name: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "name", "domain_of": ["Entity", "MultiEntityAssociationResults"]}},
    )
    full_name: Optional[str] = Field(
        None,
        description="""The long form name of an entity""",
        json_schema_extra={"linkml_meta": {"alias": "full_name", "domain_of": ["Entity"]}},
    )
    deprecated: Optional[bool] = Field(
        None,
        description="""A boolean flag indicating that an entity is no longer considered current or valid.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "deprecated",
                "domain_of": ["Entity"],
                "exact_mappings": ["oboInOwl:ObsoleteClass"],
            }
        },
    )
    description: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "description", "domain_of": ["Entity"]}}
    )
    xref: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "xref", "domain_of": ["Entity"]}}
    )
    provided_by: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "provided_by", "domain_of": ["Association", "Entity"]}}
    )
    in_taxon: Optional[str] = Field(
        None,
        description="""The biolink taxon that the entity is in the closure of.""",
        json_schema_extra={"linkml_meta": {"alias": "in_taxon", "domain_of": ["Entity", "Node"]}},
    )
    in_taxon_label: Optional[str] = Field(
        None,
        description="""The label of the biolink taxon that the entity is in the closure of.""",
        json_schema_extra={"linkml_meta": {"alias": "in_taxon_label", "domain_of": ["Entity", "Node"]}},
    )
    symbol: Optional[str] = Field(None, json_schema_extra={"linkml_meta": {"alias": "symbol", "domain_of": ["Entity"]}})
    synonym: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "synonym", "domain_of": ["Entity"]}}
    )
    broad_synonym: Optional[List[str]] = Field(
        None,
        description="""A broader synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "broad_synonym", "domain_of": ["Entity"]}},
    )
    exact_synonym: Optional[List[str]] = Field(
        None,
        description="""An exact synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "exact_synonym", "domain_of": ["Entity"]}},
    )
    narrow_synonym: Optional[List[str]] = Field(
        None,
        description="""A narrower synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "narrow_synonym", "domain_of": ["Entity"]}},
    )
    related_synonym: Optional[List[str]] = Field(
        None,
        description="""A related synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "related_synonym", "domain_of": ["Entity"]}},
    )
    subsets: Optional[List[str]] = Field(
        None,
        description="""A list of subsets that the entity belongs to""",
        json_schema_extra={"linkml_meta": {"alias": "subsets", "domain_of": ["Entity"]}},
    )
    uri: Optional[str] = Field(
        None,
        description="""The URI of the entity""",
        json_schema_extra={"linkml_meta": {"alias": "uri", "domain_of": ["Entity"]}},
    )
    iri: Optional[str] = Field(None, json_schema_extra={"linkml_meta": {"alias": "iri", "domain_of": ["Entity"]}})
    namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix portion of this entity's identifier""",
        json_schema_extra={"linkml_meta": {"alias": "namespace", "domain_of": ["Entity"]}},
    )
    has_phenotype: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype identifiers that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype", "domain_of": ["Entity"]}},
    )
    has_phenotype_label: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype labels that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_label", "domain_of": ["Entity"]}},
    )
    has_phenotype_closure: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_closure", "domain_of": ["Entity"]}},
    )
    has_phenotype_closure_label: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_closure_label", "domain_of": ["Entity"]}},
    )
    has_phenotype_count: Optional[int] = Field(
        None,
        description="""A count of the number of phenotypes that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_count", "domain_of": ["Entity"]}},
    )


class FacetValue(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    label: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "label", "domain_of": ["TermInfo", "FacetValue", "FacetField"]}},
    )
    count: Optional[int] = Field(
        None,
        description="""count of documents""",
        json_schema_extra={"linkml_meta": {"alias": "count", "domain_of": ["FacetValue"]}},
    )


class AssociationCount(FacetValue):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"category": {"multivalued": False, "name": "category"}},
        }
    )

    category: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )
    label: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "label", "domain_of": ["TermInfo", "FacetValue", "FacetField"]}},
    )
    count: Optional[int] = Field(
        None,
        description="""count of documents""",
        json_schema_extra={"linkml_meta": {"alias": "count", "domain_of": ["FacetValue"]}},
    )


class FacetField(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    label: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "label", "domain_of": ["TermInfo", "FacetValue", "FacetField"]}},
    )
    facet_values: Optional[List[FacetValue]] = Field(
        None,
        description="""Collection of FacetValue label/value instances belonging to a FacetField""",
        json_schema_extra={"linkml_meta": {"alias": "facet_values", "domain_of": ["FacetField"]}},
    )


class HistoPheno(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "HistoBin"}},
        }
    )

    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    items: List[HistoBin] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )


class HistoBin(FacetValue):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    label: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "label", "domain_of": ["TermInfo", "FacetValue", "FacetField"]}},
    )
    count: Optional[int] = Field(
        None,
        description="""count of documents""",
        json_schema_extra={"linkml_meta": {"alias": "count", "domain_of": ["FacetValue"]}},
    )


class Mapping(ConfiguredBaseModel):
    """
    A minimal class to hold a SSSOM mapping
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    subject_id: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "subject_id", "domain_of": ["TermPairwiseSimilarity", "Mapping"]}},
    )
    subject_label: Optional[str] = Field(
        None,
        description="""The name of the subject entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subject_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    predicate_id: str = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "predicate_id", "domain_of": ["Mapping"]}}
    )
    object_id: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "object_id", "domain_of": ["TermPairwiseSimilarity", "Mapping"]}},
    )
    object_label: Optional[str] = Field(
        None,
        description="""The name of the object entity""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "object_label",
                "domain_of": [
                    "TermPairwiseSimilarity",
                    "Association",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Mapping",
                ],
                "is_a": "name",
            }
        },
    )
    mapping_justification: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "mapping_justification", "domain_of": ["Mapping"]}}
    )
    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )


class Node(Entity):
    """
    UI container class extending Entity with additional information
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    in_taxon: Optional[str] = Field(
        None,
        description="""The biolink taxon that the entity is in the closure of.""",
        json_schema_extra={"linkml_meta": {"alias": "in_taxon", "domain_of": ["Entity", "Node"]}},
    )
    in_taxon_label: Optional[str] = Field(
        None,
        description="""The label of the biolink taxon that the entity is in the closure of.""",
        json_schema_extra={"linkml_meta": {"alias": "in_taxon_label", "domain_of": ["Entity", "Node"]}},
    )
    inheritance: Optional[Entity] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "inheritance", "domain_of": ["Node"]}}
    )
    causal_gene: Optional[List[Entity]] = Field(
        None,
        description="""A list of genes that are known to be causally associated with a disease""",
        json_schema_extra={"linkml_meta": {"alias": "causal_gene", "domain_of": ["Node"]}},
    )
    causes_disease: Optional[List[Entity]] = Field(
        None,
        description="""A list of diseases that are known to be causally associated with a gene""",
        json_schema_extra={"linkml_meta": {"alias": "causes_disease", "domain_of": ["Node"]}},
    )
    mappings: Optional[List[ExpandedCurie]] = Field(
        None,
        description="""List of ExpandedCuries with id and url for mapped entities""",
        json_schema_extra={"linkml_meta": {"alias": "mappings", "domain_of": ["Node"]}},
    )
    external_links: Optional[List[ExpandedCurie]] = Field(
        None,
        description="""ExpandedCurie with id and url for xrefs""",
        json_schema_extra={"linkml_meta": {"alias": "external_links", "domain_of": ["Node"]}},
    )
    provided_by_link: Optional[ExpandedCurie] = Field(
        None,
        description="""A link to the docs for the knowledge source that provided the node/edge.""",
        json_schema_extra={"linkml_meta": {"alias": "provided_by_link", "domain_of": ["Association", "Node"]}},
    )
    association_counts: List[AssociationCount] = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "association_counts", "domain_of": ["Node"]}}
    )
    node_hierarchy: Optional[NodeHierarchy] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "node_hierarchy", "domain_of": ["Node"]}}
    )
    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    category: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )
    name: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "name", "domain_of": ["Entity", "MultiEntityAssociationResults"]}},
    )
    full_name: Optional[str] = Field(
        None,
        description="""The long form name of an entity""",
        json_schema_extra={"linkml_meta": {"alias": "full_name", "domain_of": ["Entity"]}},
    )
    deprecated: Optional[bool] = Field(
        None,
        description="""A boolean flag indicating that an entity is no longer considered current or valid.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "deprecated",
                "domain_of": ["Entity"],
                "exact_mappings": ["oboInOwl:ObsoleteClass"],
            }
        },
    )
    description: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "description", "domain_of": ["Entity"]}}
    )
    xref: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "xref", "domain_of": ["Entity"]}}
    )
    provided_by: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "provided_by", "domain_of": ["Association", "Entity"]}}
    )
    symbol: Optional[str] = Field(None, json_schema_extra={"linkml_meta": {"alias": "symbol", "domain_of": ["Entity"]}})
    synonym: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "synonym", "domain_of": ["Entity"]}}
    )
    broad_synonym: Optional[List[str]] = Field(
        None,
        description="""A broader synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "broad_synonym", "domain_of": ["Entity"]}},
    )
    exact_synonym: Optional[List[str]] = Field(
        None,
        description="""An exact synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "exact_synonym", "domain_of": ["Entity"]}},
    )
    narrow_synonym: Optional[List[str]] = Field(
        None,
        description="""A narrower synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "narrow_synonym", "domain_of": ["Entity"]}},
    )
    related_synonym: Optional[List[str]] = Field(
        None,
        description="""A related synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "related_synonym", "domain_of": ["Entity"]}},
    )
    subsets: Optional[List[str]] = Field(
        None,
        description="""A list of subsets that the entity belongs to""",
        json_schema_extra={"linkml_meta": {"alias": "subsets", "domain_of": ["Entity"]}},
    )
    uri: Optional[str] = Field(
        None,
        description="""The URI of the entity""",
        json_schema_extra={"linkml_meta": {"alias": "uri", "domain_of": ["Entity"]}},
    )
    iri: Optional[str] = Field(None, json_schema_extra={"linkml_meta": {"alias": "iri", "domain_of": ["Entity"]}})
    namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix portion of this entity's identifier""",
        json_schema_extra={"linkml_meta": {"alias": "namespace", "domain_of": ["Entity"]}},
    )
    has_phenotype: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype identifiers that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype", "domain_of": ["Entity"]}},
    )
    has_phenotype_label: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype labels that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_label", "domain_of": ["Entity"]}},
    )
    has_phenotype_closure: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_closure", "domain_of": ["Entity"]}},
    )
    has_phenotype_closure_label: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_closure_label", "domain_of": ["Entity"]}},
    )
    has_phenotype_count: Optional[int] = Field(
        None,
        description="""A count of the number of phenotypes that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_count", "domain_of": ["Entity"]}},
    )


class NodeHierarchy(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    super_classes: List[Entity] = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "super_classes", "domain_of": ["NodeHierarchy"]}}
    )
    sub_classes: List[Entity] = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "sub_classes", "domain_of": ["NodeHierarchy"]}}
    )


class Release(ConfiguredBaseModel):
    """
    A class to hold information about a release of the Monarch KG
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    version: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "version", "domain_of": ["Release"], "id_prefixes": ["string"]}},
    )
    url: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "url", "domain_of": ["ExpandedCurie", "Release"]}}
    )
    kg: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "kg", "domain_of": ["Release"], "id_prefixes": ["string"]}}
    )
    sqlite: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "sqlite", "domain_of": ["Release"], "id_prefixes": ["string"]}},
    )
    solr: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "solr", "domain_of": ["Release"], "id_prefixes": ["string"]}}
    )
    neo4j: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "neo4j", "domain_of": ["Release"], "id_prefixes": ["string"]}}
    )
    metadata: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "metadata", "domain_of": ["Release"], "id_prefixes": ["string"]}},
    )
    graph_stats: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "graph_stats", "domain_of": ["Release"], "id_prefixes": ["string"]}
        },
    )
    qc_report: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "qc_report", "domain_of": ["Release"], "id_prefixes": ["string"]}},
    )


class Results(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"abstract": True, "from_schema": "https://w3id.org/monarch/monarch-py"}
    )

    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class AssociationResults(Results):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "Association"}},
        }
    )

    items: List[Association] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_fields: Optional[List[FacetField]] = Field(
        None,
        description="""Collection of facet field responses with the field values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_fields",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_queries: Optional[List[FacetValue]] = Field(
        None,
        description="""Collection of facet query responses with the query string values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_queries",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class CompactAssociationResults(Results):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "CompactAssociation"}},
        }
    )

    items: List[CompactAssociation] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_fields: Optional[List[FacetField]] = Field(
        None,
        description="""Collection of facet field responses with the field values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_fields",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_queries: Optional[List[FacetValue]] = Field(
        None,
        description="""Collection of facet query responses with the query string values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_queries",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class AssociationTableResults(Results):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "DirectionalAssociation"}},
        }
    )

    items: List[DirectionalAssociation] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_fields: Optional[List[FacetField]] = Field(
        None,
        description="""Collection of facet field responses with the field values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_fields",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_queries: Optional[List[FacetValue]] = Field(
        None,
        description="""Collection of facet query responses with the query string values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_queries",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class CategoryGroupedAssociationResults(Results):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "Association"}},
        }
    )

    counterpart_category: Optional[str] = Field(
        None,
        description="""The category of the counterpart entity in a given association,  eg. the category of the entity that is not the subject""",
        json_schema_extra={
            "linkml_meta": {"alias": "counterpart_category", "domain_of": ["CategoryGroupedAssociationResults"]}
        },
    )
    items: List[Association] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class EntityResults(Results):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "Entity"}},
        }
    )

    items: List[Entity] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class MappingResults(Results):
    """
    SSSOM Mappings returned as a results collection
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "Mapping"}},
        }
    )

    items: List[Mapping] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class MultiEntityAssociationResults(Results):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    name: Optional[str] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "name", "domain_of": ["Entity", "MultiEntityAssociationResults"]}},
    )
    associated_categories: List[CategoryGroupedAssociationResults] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {"alias": "associated_categories", "domain_of": ["MultiEntityAssociationResults"]}
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class SearchResult(Entity):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {
                "category": {"name": "category", "required": True},
                "name": {"name": "name", "required": True},
            },
        }
    )

    score: Optional[float] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "score", "domain_of": ["BestMatch", "SemsimSearchResult", "SearchResult"]}
        },
    )
    id: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": [
                    "TermInfo",
                    "Association",
                    "ExpandedCurie",
                    "Entity",
                    "HistoPheno",
                    "HistoBin",
                    "Mapping",
                    "MultiEntityAssociationResults",
                ],
            }
        },
    )
    category: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "category",
                "domain_of": [
                    "Association",
                    "AssociationCount",
                    "CompactAssociation",
                    "AssociationTypeMapping",
                    "Entity",
                ],
            }
        },
    )
    name: str = Field(
        ...,
        json_schema_extra={"linkml_meta": {"alias": "name", "domain_of": ["Entity", "MultiEntityAssociationResults"]}},
    )
    full_name: Optional[str] = Field(
        None,
        description="""The long form name of an entity""",
        json_schema_extra={"linkml_meta": {"alias": "full_name", "domain_of": ["Entity"]}},
    )
    deprecated: Optional[bool] = Field(
        None,
        description="""A boolean flag indicating that an entity is no longer considered current or valid.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "deprecated",
                "domain_of": ["Entity"],
                "exact_mappings": ["oboInOwl:ObsoleteClass"],
            }
        },
    )
    description: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "description", "domain_of": ["Entity"]}}
    )
    xref: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "xref", "domain_of": ["Entity"]}}
    )
    provided_by: Optional[str] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "provided_by", "domain_of": ["Association", "Entity"]}}
    )
    in_taxon: Optional[str] = Field(
        None,
        description="""The biolink taxon that the entity is in the closure of.""",
        json_schema_extra={"linkml_meta": {"alias": "in_taxon", "domain_of": ["Entity", "Node"]}},
    )
    in_taxon_label: Optional[str] = Field(
        None,
        description="""The label of the biolink taxon that the entity is in the closure of.""",
        json_schema_extra={"linkml_meta": {"alias": "in_taxon_label", "domain_of": ["Entity", "Node"]}},
    )
    symbol: Optional[str] = Field(None, json_schema_extra={"linkml_meta": {"alias": "symbol", "domain_of": ["Entity"]}})
    synonym: Optional[List[str]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "synonym", "domain_of": ["Entity"]}}
    )
    broad_synonym: Optional[List[str]] = Field(
        None,
        description="""A broader synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "broad_synonym", "domain_of": ["Entity"]}},
    )
    exact_synonym: Optional[List[str]] = Field(
        None,
        description="""An exact synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "exact_synonym", "domain_of": ["Entity"]}},
    )
    narrow_synonym: Optional[List[str]] = Field(
        None,
        description="""A narrower synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "narrow_synonym", "domain_of": ["Entity"]}},
    )
    related_synonym: Optional[List[str]] = Field(
        None,
        description="""A related synonym for the entity""",
        json_schema_extra={"linkml_meta": {"alias": "related_synonym", "domain_of": ["Entity"]}},
    )
    subsets: Optional[List[str]] = Field(
        None,
        description="""A list of subsets that the entity belongs to""",
        json_schema_extra={"linkml_meta": {"alias": "subsets", "domain_of": ["Entity"]}},
    )
    uri: Optional[str] = Field(
        None,
        description="""The URI of the entity""",
        json_schema_extra={"linkml_meta": {"alias": "uri", "domain_of": ["Entity"]}},
    )
    iri: Optional[str] = Field(None, json_schema_extra={"linkml_meta": {"alias": "iri", "domain_of": ["Entity"]}})
    namespace: Optional[str] = Field(
        None,
        description="""The namespace/prefix portion of this entity's identifier""",
        json_schema_extra={"linkml_meta": {"alias": "namespace", "domain_of": ["Entity"]}},
    )
    has_phenotype: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype identifiers that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype", "domain_of": ["Entity"]}},
    )
    has_phenotype_label: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype labels that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_label", "domain_of": ["Entity"]}},
    )
    has_phenotype_closure: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype identifiers that are known to be associated with this entity expanded to include all ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_closure", "domain_of": ["Entity"]}},
    )
    has_phenotype_closure_label: Optional[List[str]] = Field(
        None,
        description="""A list of phenotype labels that are known to be associated with this entity expanded to include all ancestors""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_closure_label", "domain_of": ["Entity"]}},
    )
    has_phenotype_count: Optional[int] = Field(
        None,
        description="""A count of the number of phenotypes that are known to be associated with this entity""",
        json_schema_extra={"linkml_meta": {"alias": "has_phenotype_count", "domain_of": ["Entity"]}},
    )


class SearchResults(Results):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/monarch/monarch-py",
            "slot_usage": {"items": {"name": "items", "range": "SearchResult"}},
        }
    )

    items: List[SearchResult] = Field(
        ...,
        description="""A collection of items, with the type to be overriden by slot_usage""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "items",
                "domain_of": [
                    "AssociationCountList",
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "CategoryGroupedAssociationResults",
                    "EntityResults",
                    "HistoPheno",
                    "MappingResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_fields: Optional[List[FacetField]] = Field(
        None,
        description="""Collection of facet field responses with the field values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_fields",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    facet_queries: Optional[List[FacetValue]] = Field(
        None,
        description="""Collection of facet query responses with the query string values and counts""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "facet_queries",
                "domain_of": [
                    "AssociationResults",
                    "CompactAssociationResults",
                    "AssociationTableResults",
                    "SearchResults",
                ],
            }
        },
    )
    limit: int = Field(
        ...,
        description="""number of items to return in a response""",
        json_schema_extra={"linkml_meta": {"alias": "limit", "domain_of": ["Results"]}},
    )
    offset: int = Field(
        ...,
        description="""offset into the total number of items""",
        json_schema_extra={"linkml_meta": {"alias": "offset", "domain_of": ["Results"]}},
    )
    total: int = Field(
        ...,
        description="""total number of items matching a query""",
        json_schema_extra={"linkml_meta": {"alias": "total", "domain_of": ["Results"]}},
    )


class TextAnnotationResult(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "https://w3id.org/monarch/monarch-py"})

    text: Optional[str] = Field(
        None,
        description="""text without tokens""",
        json_schema_extra={"linkml_meta": {"alias": "text", "domain_of": ["TextAnnotationResult"]}},
    )
    tokens: Optional[List[Entity]] = Field(
        None,
        description="""A collection of entities or concepts""",
        json_schema_extra={"linkml_meta": {"alias": "tokens", "domain_of": ["TextAnnotationResult"]}},
    )
    start: Optional[int] = Field(
        None,
        description="""start position of the annotation""",
        json_schema_extra={"linkml_meta": {"alias": "start", "domain_of": ["TextAnnotationResult"]}},
    )
    end: Optional[int] = Field(
        None,
        description="""end position of the annotation""",
        json_schema_extra={"linkml_meta": {"alias": "end", "domain_of": ["TextAnnotationResult"]}},
    )


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
