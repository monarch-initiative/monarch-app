export type AssociationId = string;
export type DirectionalAssociationId = string;
export type ExpandedCurieId = string;
export type EntityId = string;
export type HistoPhenoId = string;
export type HistoBinId = string;
export type NodeId = string;
export type SearchResultId = string;
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
    category?: string,
    negated?: boolean,
    provided_by?: string,
    publications?: string[],
    qualifiers?: string[],
    frequency_qualifier?: string,
    has_evidence?: string[],
    onset_qualifier?: string,
    sex_qualifier?: string,
    stage_qualifier?: string,
    /** count of supporting documents, evidence codes, and sources supplying evidence */
    evidence_count?: number,
    pathway?: string,
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
/**
 * An association that gives it's direction relative to a specified entity
 */
export interface DirectionalAssociation extends Association {
    /** The directionality of the association relative to a given entity for an association_count. If the entity is the subject or in the subject closure, the direction is forwards, if it is the object or in the object closure, the direction is backwards. */
    direction: string,
    id: string,
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
    category?: string,
    negated?: boolean,
    provided_by?: string,
    publications?: string[],
    qualifiers?: string[],
    frequency_qualifier?: string,
    has_evidence?: string[],
    onset_qualifier?: string,
    sex_qualifier?: string,
    stage_qualifier?: string,
    /** count of supporting documents, evidence codes, and sources supplying evidence */
    evidence_count?: number,
    pathway?: string,
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
 * UI container class extending Entity with additional information
 */
export interface Node extends Entity {
    /** The biolink taxon that the entity is in the closure of. */
    in_taxon?: string,
    /** The label of the biolink taxon that the entity is in the closure of. */
    in_taxon_label?: string,
    inheritance?: Entity,
    /** Expanded Curie with id and url for xrefs */
    external_links?: ExpandedCurie[],
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
};

export interface NodeHierarchy {
    super_classes: Entity[],
    equivalent_classes: Entity[],
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

