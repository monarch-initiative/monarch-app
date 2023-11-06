export type AssociationId = string;
export type DirectionalAssociationId = string;
export type ExpandedCurieId = string;
export type EntityId = string;
export type HistoPhenoId = string;
export type HistoBinId = string;
export type MultiEntityAssociationResultsId = string;
export type NodeId = string;
export type SearchResultId = string;
export type TermInfoId = string;
export type BestMatchMatchSource = string;
/**
* The directionality of an association as it relates to a specified entity, with edges being categorized as incoming or outgoing
*/
export enum AssociationDirectionEnum {
    
    /** An association for which a specified entity is the object or part of the object closure */
    incoming = "incoming",
    /** An association for which a specified entity is the subject or part of the subject closure */
    outgoing = "outgoing",
};



export interface Association {
    id: string,
    category?: string,
    subject: string,
    original_subject?: string,
    /** The namespace/prefix of the subject entity */
    subject_namespace?: string,
    /** The category of the subject entity */
    subject_category?: string,
    /** Field containing subject id and the ids of all of it's ancestors */
    subject_closure?: string[],
    /** The name of the subject entity */
    subject_label?: string,
    /** Field containing subject name and the names of all of it's ancestors */
    subject_closure_label?: string[],
    subject_taxon?: string,
    subject_taxon_label?: string,
    predicate: string,
    object: string,
    original_object?: string,
    /** The namespace/prefix of the object entity */
    object_namespace?: string,
    /** The category of the object entity */
    object_category?: string,
    /** Field containing object id and the ids of all of it's ancestors */
    object_closure?: string[],
    /** The name of the object entity */
    object_label?: string,
    /** Field containing object name and the names of all of it's ancestors */
    object_closure_label?: string[],
    object_taxon?: string,
    object_taxon_label?: string,
    primary_knowledge_source?: string,
    aggregator_knowledge_source?: string[],
    negated?: boolean,
    pathway?: string,
    /** count of supporting documents, evidence codes, and sources supplying evidence */
    evidence_count?: number,
    has_evidence?: string[],
    /** List of ExpandedCuries with id and url for evidence */
    has_evidence_links?: ExpandedCurie[],
    /** A concatenation of fields used to group associations with the same essential/defining properties */
    grouping_key?: string,
    provided_by?: string,
    /** A link to the docs for the knowledge source that provided the node/edge. */
    provided_by_link?: ExpandedCurie,
    publications?: string[],
    /** List of ExpandedCuries with id and url for publications */
    publications_links?: ExpandedCurie[],
    qualifiers?: string[],
    frequency_qualifier?: string,
    onset_qualifier?: string,
    sex_qualifier?: string,
    stage_qualifier?: string,
    /** The name of the frequency_qualifier entity */
    qualifiers_label?: string,
    /** The namespace/prefix of the frequency_qualifier entity */
    qualifiers_namespace?: string,
    /** The category of the frequency_qualifier entity */
    qualifiers_category?: string,
    /** Field containing frequency_qualifier id and the ids of all of it's ancestors */
    qualifiers_closure?: string[],
    /** Field containing frequency_qualifier name and the names of all of it's ancestors */
    qualifiers_closure_label?: string[],
    /** The name of the frequency_qualifier entity */
    frequency_qualifier_label?: string,
    /** The namespace/prefix of the frequency_qualifier entity */
    frequency_qualifier_namespace?: string,
    /** The category of the frequency_qualifier entity */
    frequency_qualifier_category?: string,
    /** Field containing frequency_qualifier id and the ids of all of it's ancestors */
    frequency_qualifier_closure?: string[],
    /** Field containing frequency_qualifier name and the names of all of it's ancestors */
    frequency_qualifier_closure_label?: string[],
    /** The name of the onset_qualifier entity */
    onset_qualifier_label?: string,
    /** The namespace/prefix of the onset_qualifier entity */
    onset_qualifier_namespace?: string,
    /** The category of the onset_qualifier entity */
    onset_qualifier_category?: string,
    /** Field containing onset_qualifier id and the ids of all of it's ancestors */
    onset_qualifier_closure?: string[],
    /** Field containing onset_qualifier name and the names of all of it's ancestors */
    onset_qualifier_closure_label?: string[],
    /** The name of the sex_qualifier entity */
    sex_qualifier_label?: string,
    /** The namespace/prefix of the sex_qualifier entity */
    sex_qualifier_namespace?: string,
    /** The category of the sex_qualifier entity */
    sex_qualifier_category?: string,
    /** Field containing sex_qualifier id and the ids of all of it's ancestors */
    sex_qualifier_closure?: string[],
    /** Field containing sex_qualifier name and the names of all of it's ancestors */
    sex_qualifier_closure_label?: string[],
    /** The name of the stage_qualifier entity */
    stage_qualifier_label?: string,
    /** The namespace/prefix of the stage_qualifier entity */
    stage_qualifier_namespace?: string,
    /** The category of the stage_qualifier entity */
    stage_qualifier_category?: string,
    /** Field containing stage_qualifier id and the ids of all of it's ancestors */
    stage_qualifier_closure?: string[],
    /** Field containing stage_qualifier name and the names of all of it's ancestors */
    stage_qualifier_closure_label?: string[],
};

export interface AssociationCount extends FacetValue {
    category?: string,
    label: string,
    /** count of documents */
    count?: number,
};
/**
 * Container class for a list of association counts
 */
export interface AssociationCountList {
    /** A collection of items, with the type to be overriden by slot_usage */
    items: AssociationCount[],
};

export interface AssociationResults extends Results {
    /** A collection of items, with the type to be overriden by slot_usage */
    items: Association[],
    /** number of items to return in a response */
    limit: number,
    /** offset into the total number of items */
    offset: number,
    /** total number of items matching a query */
    total: number,
};

export interface AssociationTableResults extends Results {
    /** A collection of items, with the type to be overriden by slot_usage */
    items: DirectionalAssociation[],
    /** number of items to return in a response */
    limit: number,
    /** offset into the total number of items */
    offset: number,
    /** total number of items matching a query */
    total: number,
};
/**
 * A data class to hold the necessary information to produce association type counts for given  entities with appropriate directional labels
 */
export interface AssociationTypeMapping {
    /** A label to describe the subjects of the association type as a whole for use in the UI */
    subject_label?: string,
    /** A label to describe the objects of the association type as a whole for use in the UI */
    object_label?: string,
    /** Whether the association type is symmetric, meaning that the subject and object labels should be interchangeable */
    symmetric: boolean,
    /** The biolink category to use in queries for this association type */
    category: string,
};

export interface CategoryGroupedAssociationResults extends Results {
    /** The category of the counterpart entity in a given association,  eg. the category of the entity that is not the subject */
    counterpart_category?: string,
    /** A collection of items, with the type to be overriden by slot_usage */
    items: Association[],
    /** number of items to return in a response */
    limit: number,
    /** offset into the total number of items */
    offset: number,
    /** total number of items matching a query */
    total: number,
};
/**
 * An association that gives it's direction relative to a specified entity
 */
export interface DirectionalAssociation extends Association {
    /** The directionality of the association relative to a given entity for an association_count. If the entity is the subject or in the subject closure, the direction is forwards, if it is the object or in the object closure, the direction is backwards. */
    direction: string,
    id: string,
    category?: string,
    subject: string,
    original_subject?: string,
    /** The namespace/prefix of the subject entity */
    subject_namespace?: string,
    /** The category of the subject entity */
    subject_category?: string,
    /** Field containing subject id and the ids of all of it's ancestors */
    subject_closure?: string[],
    /** The name of the subject entity */
    subject_label?: string,
    /** Field containing subject name and the names of all of it's ancestors */
    subject_closure_label?: string[],
    subject_taxon?: string,
    subject_taxon_label?: string,
    predicate: string,
    object: string,
    original_object?: string,
    /** The namespace/prefix of the object entity */
    object_namespace?: string,
    /** The category of the object entity */
    object_category?: string,
    /** Field containing object id and the ids of all of it's ancestors */
    object_closure?: string[],
    /** The name of the object entity */
    object_label?: string,
    /** Field containing object name and the names of all of it's ancestors */
    object_closure_label?: string[],
    object_taxon?: string,
    object_taxon_label?: string,
    primary_knowledge_source?: string,
    aggregator_knowledge_source?: string[],
    negated?: boolean,
    pathway?: string,
    /** count of supporting documents, evidence codes, and sources supplying evidence */
    evidence_count?: number,
    has_evidence?: string[],
    /** List of ExpandedCuries with id and url for evidence */
    has_evidence_links?: ExpandedCurie[],
    /** A concatenation of fields used to group associations with the same essential/defining properties */
    grouping_key?: string,
    provided_by?: string,
    /** A link to the docs for the knowledge source that provided the node/edge. */
    provided_by_link?: ExpandedCurie,
    publications?: string[],
    /** List of ExpandedCuries with id and url for publications */
    publications_links?: ExpandedCurie[],
    qualifiers?: string[],
    frequency_qualifier?: string,
    onset_qualifier?: string,
    sex_qualifier?: string,
    stage_qualifier?: string,
    /** The name of the frequency_qualifier entity */
    qualifiers_label?: string,
    /** The namespace/prefix of the frequency_qualifier entity */
    qualifiers_namespace?: string,
    /** The category of the frequency_qualifier entity */
    qualifiers_category?: string,
    /** Field containing frequency_qualifier id and the ids of all of it's ancestors */
    qualifiers_closure?: string[],
    /** Field containing frequency_qualifier name and the names of all of it's ancestors */
    qualifiers_closure_label?: string[],
    /** The name of the frequency_qualifier entity */
    frequency_qualifier_label?: string,
    /** The namespace/prefix of the frequency_qualifier entity */
    frequency_qualifier_namespace?: string,
    /** The category of the frequency_qualifier entity */
    frequency_qualifier_category?: string,
    /** Field containing frequency_qualifier id and the ids of all of it's ancestors */
    frequency_qualifier_closure?: string[],
    /** Field containing frequency_qualifier name and the names of all of it's ancestors */
    frequency_qualifier_closure_label?: string[],
    /** The name of the onset_qualifier entity */
    onset_qualifier_label?: string,
    /** The namespace/prefix of the onset_qualifier entity */
    onset_qualifier_namespace?: string,
    /** The category of the onset_qualifier entity */
    onset_qualifier_category?: string,
    /** Field containing onset_qualifier id and the ids of all of it's ancestors */
    onset_qualifier_closure?: string[],
    /** Field containing onset_qualifier name and the names of all of it's ancestors */
    onset_qualifier_closure_label?: string[],
    /** The name of the sex_qualifier entity */
    sex_qualifier_label?: string,
    /** The namespace/prefix of the sex_qualifier entity */
    sex_qualifier_namespace?: string,
    /** The category of the sex_qualifier entity */
    sex_qualifier_category?: string,
    /** Field containing sex_qualifier id and the ids of all of it's ancestors */
    sex_qualifier_closure?: string[],
    /** Field containing sex_qualifier name and the names of all of it's ancestors */
    sex_qualifier_closure_label?: string[],
    /** The name of the stage_qualifier entity */
    stage_qualifier_label?: string,
    /** The namespace/prefix of the stage_qualifier entity */
    stage_qualifier_namespace?: string,
    /** The category of the stage_qualifier entity */
    stage_qualifier_category?: string,
    /** Field containing stage_qualifier id and the ids of all of it's ancestors */
    stage_qualifier_closure?: string[],
    /** Field containing stage_qualifier name and the names of all of it's ancestors */
    stage_qualifier_closure_label?: string[],
};
/**
 * A curie bundled along with its expanded url
 */
export interface ExpandedCurie {
    id: string,
    url?: string,
};
/**
 * Represents an Entity in the Monarch KG data model
 */
export interface Entity {
    id: string,
    category?: string,
    name?: string,
    /** The long form name of an entity */
    full_name?: string,
    description?: string,
    xref?: string[],
    provided_by?: string,
    /** The biolink taxon that the entity is in the closure of. */
    in_taxon?: string,
    /** The label of the biolink taxon that the entity is in the closure of. */
    in_taxon_label?: string,
    symbol?: string,
    synonym?: string[],
    /** The URI of the entity */
    uri?: string,
};

export interface EntityResults extends Results {
    /** A collection of items, with the type to be overriden by slot_usage */
    items: Entity[],
    /** number of items to return in a response */
    limit: number,
    /** offset into the total number of items */
    offset: number,
    /** total number of items matching a query */
    total: number,
};

export interface FacetValue {
    label: string,
    /** count of documents */
    count?: number,
};

export interface FacetField {
    label: string,
    /** Collection of FacetValue label/value instances belonging to a FacetField */
    facet_values?: FacetValue[],
};

export interface HistoPheno {
    id: string,
    /** A collection of items, with the type to be overriden by slot_usage */
    items: HistoBin[],
};

export interface HistoBin extends FacetValue {
    id: string,
    label: string,
    /** count of documents */
    count?: number,
};
/**
 * A minimal class to hold a SSSOM mapping
 */
export interface Mapping {
    subject_id: string,
    /** The name of the subject entity */
    subject_label?: string,
    predicate_id: string,
    object_id: string,
    /** The name of the object entity */
    object_label?: string,
    mapping_justification?: string,
};

export interface MultiEntityAssociationResults extends Results {
    id: string,
    name?: string,
    associated_categories: CategoryGroupedAssociationResults[],
    /** number of items to return in a response */
    limit: number,
    /** offset into the total number of items */
    offset: number,
    /** total number of items matching a query */
    total: number,
};
/**
 * UI container class extending Entity with additional information
 */
export interface Node extends Entity {
    /** The biolink taxon that the entity is in the closure of. */
    in_taxon?: string,
    /** The label of the biolink taxon that the entity is in the closure of. */
    in_taxon_label?: string,
    inheritance?: Entity,
    /** A list of genes that are known to be causally associated with a disease */
    causal_gene?: Entity[],
    /** A list of diseases that are known to be causally associated with a gene */
    causes_disease?: Entity[],
    /** ExpandedCurie with id and url for xrefs */
    external_links?: ExpandedCurie[],
    /** A link to the docs for the knowledge source that provided the node/edge. */
    provided_by_link?: ExpandedCurie,
    association_counts: AssociationCount[],
    node_hierarchy?: NodeHierarchy,
    id: string,
    category?: string,
    name?: string,
    /** The long form name of an entity */
    full_name?: string,
    description?: string,
    xref?: string[],
    provided_by?: string,
    symbol?: string,
    synonym?: string[],
    /** The URI of the entity */
    uri?: string,
};

export interface NodeHierarchy {
    super_classes: Entity[],
    sub_classes: Entity[],
};

export interface Results {
    /** number of items to return in a response */
    limit: number,
    /** offset into the total number of items */
    offset: number,
    /** total number of items matching a query */
    total: number,
};

export interface SearchResult extends Entity {
    /** matching text snippet containing html tags */
    highlight?: string,
    score?: number,
    id: string,
    category: string,
    name: string,
    /** The long form name of an entity */
    full_name?: string,
    description?: string,
    xref?: string[],
    provided_by?: string,
    /** The biolink taxon that the entity is in the closure of. */
    in_taxon?: string,
    /** The label of the biolink taxon that the entity is in the closure of. */
    in_taxon_label?: string,
    symbol?: string,
    synonym?: string[],
    /** The URI of the entity */
    uri?: string,
};

export interface SearchResults extends Results {
    /** A collection of items, with the type to be overriden by slot_usage */
    items: SearchResult[],
    /** Collection of facet field responses with the field values and counts */
    facet_fields?: FacetField[],
    /** Collection of facet query responses with the query string values and counts */
    facet_queries?: FacetValue[],
    /** number of items to return in a response */
    limit: number,
    /** offset into the total number of items */
    offset: number,
    /** total number of items matching a query */
    total: number,
};
/**
 * Abstract grouping for representing individual pairwise similarities
 */
export interface PairwiseSimilarity {
};
/**
 * A simple pairwise similarity between two atomic concepts/terms
 */
export interface TermPairwiseSimilarity extends PairwiseSimilarity {
    subject_id: string,
    /** The name of the subject entity */
    subject_label?: string,
    /** the source for the first entity */
    subject_source?: string,
    object_id: string,
    /** The name of the object entity */
    object_label?: string,
    /** the source for the second entity */
    object_source?: string,
    /** the most recent common ancestor of the two compared entities. If there are multiple MRCAs then the most informative one is selected */
    ancestor_id?: string,
    /** the name or label of the ancestor concept */
    ancestor_label?: string,
    ancestor_source?: string,
    /** The IC of the object */
    object_information_content?: string,
    /** The IC of the subject */
    subject_information_content?: string,
    /** The IC of the object */
    ancestor_information_content?: string,
    /** The number of concepts in the intersection divided by the number in the union */
    jaccard_similarity?: number,
    /** the dot product of two node embeddings divided by the product of their lengths */
    cosine_similarity?: number,
    dice_similarity?: number,
    /** the geometric mean of the jaccard similarity and the information content */
    phenodigm_score?: number,
};
/**
 * A simple pairwise similarity between two sets of concepts/terms
 */
export interface TermSetPairwiseSimilarity extends PairwiseSimilarity {
    subject_termset?: {[index: TermInfoId]: TermInfo },
    object_termset?: {[index: TermInfoId]: TermInfo },
    subject_best_matches?: {[index: BestMatchMatchSource]: BestMatch },
    object_best_matches?: {[index: BestMatchMatchSource]: BestMatch },
    average_score?: number,
    best_score?: number,
    metric?: string,
};

export interface TermInfo {
    id: string,
    label?: string,
};

export interface BestMatch {
    match_source: string,
    match_source_label?: string,
    /** the entity matches */
    match_target?: string,
    match_target_label?: string,
    score: number,
    match_subsumer?: string,
    match_subsumer_label?: string,
    similarity: TermPairwiseSimilarity,
};

