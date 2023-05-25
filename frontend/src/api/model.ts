export type NodeId = string;
export type TaxonId = string;
export type AssociationId = string;
export type DirectionalAssociationId = string;
export type EntityId = string;
export type HistoPhenoId = string;
export type HistoBinId = string;
export type SearchResultId = string;
export type FacetValueLabel = string;
export type FacetFieldLabel = string;
export type AssociationCountLabel = string;
/**
* The directionality of an association as it relates to a specified entity, with edges being categorized as incoming or outgoing
*/
export enum AssociationDirectionEnum {
    
    /** An association for which a specified entity is the object or part of the object closure */
    incoming = "incoming",
    /** An association for which a specified entity is the subject or part of the subject closure */
    outgoing = "outgoing",
};
/**
* A grouping label for association types, which are not necessarily 1:1 with biolink categories or predicates
*/
export enum AssociationTypeEnum {
    
    /** Any association between a disease and a phenotype */
    disease_phenotype = "disease_phenotype",
    /** Any association between a gene and a phenotype */
    gene_phenotype = "gene_phenotype",
    /** Any association between two genes */
    gene_interaction = "gene_interaction",
    /** Any association between a gene and a pathway */
    gene_pathway = "gene_pathway",
    /** Expression association between a gene and an expression site */
    gene_expression = "gene_expression",
    /** Any association between two genes based on orthology */
    gene_orthology = "gene_orthology",
    /** Any association between a chemical and a pathway */
    chemical_pathway = "chemical_pathway",
    /** Any association between a gene and molecular activity */
    gene_function = "gene_function",
    /** Association between a gene and a disease that has not been established to be causal */
    correlated_gene = "correlated_gene",
    /** Association between a gene and a disease that is known to be causal */
    causal_gene = "causal_gene",
};



export interface Node extends Entity {
    taxon?: Taxon,
    inheritance?: Entity,
    association_counts?: AssociationCount[],
    node_hierarchy?: NodeHierarchy,
    id: string,
    category?: string[],
    name?: string,
    description?: string,
    xref?: string[],
    provided_by?: string,
    in_taxon?: string,
    source?: string,
    symbol?: string,
    type?: string,
    synonym?: string[],
};

export interface Taxon {
    id: string,
    label: string,
};

export interface NodeHierarchy {
    super_classes?: Entity[],
    equivalent_classes?: Entity[],
    sub_classes?: Entity[],
};

export interface Association {
    aggregator_knowledge_source?: string[],
    id: string,
    subject: string,
    original_subject?: string,
    subject_namespace?: string,
    subject_category?: string[],
    subject_closure?: string[],
    subject_label?: string,
    subject_closure_label?: string[],
    predicate: string,
    object: string,
    original_object?: string,
    object_namespace?: string,
    object_category?: string[],
    object_closure?: string[],
    object_label?: string,
    object_closure_label?: string[],
    primary_knowledge_source?: string[],
    category?: string[],
    negated?: boolean,
    provided_by?: string,
    publications?: string[],
    qualifiers?: string[],
    frequency_qualifier?: string,
    has_evidence?: string,
    onset_qualifier?: string,
    sex_qualifier?: string,
    source?: string,
    stage_qualifier?: string,
    pathway?: string,
    relation?: string,
};
/**
 * An association that gives it's direction relative to a specified entity
 */
export interface DirectionalAssociation extends Association {
    /** The directionality of the association relative to a given entity for an association_count. If the entity is the subject or in the subject closure, the direction is forwards, if it is the object or in the object closure, the direction is backwards. */
    direction: string,
    aggregator_knowledge_source?: string[],
    id: string,
    subject: string,
    original_subject?: string,
    subject_namespace?: string,
    subject_category?: string[],
    subject_closure?: string[],
    subject_label?: string,
    subject_closure_label?: string[],
    predicate: string,
    object: string,
    original_object?: string,
    object_namespace?: string,
    object_category?: string[],
    object_closure?: string[],
    object_label?: string,
    object_closure_label?: string[],
    primary_knowledge_source?: string[],
    category?: string[],
    negated?: boolean,
    provided_by?: string,
    publications?: string[],
    qualifiers?: string[],
    frequency_qualifier?: string,
    has_evidence?: string,
    onset_qualifier?: string,
    sex_qualifier?: string,
    source?: string,
    stage_qualifier?: string,
    pathway?: string,
    relation?: string,
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

export interface Entity {
    id: string,
    category?: string[],
    name?: string,
    description?: string,
    xref?: string[],
    provided_by?: string,
    in_taxon?: string,
    source?: string,
    symbol?: string,
    type?: string,
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
    category: string[],
    name: string,
    description?: string,
    xref?: string[],
    provided_by?: string,
    in_taxon?: string,
    source?: string,
    symbol?: string,
    type?: string,
    synonym?: string[],
};

export interface SearchResults extends Results {
    /** A collection of items, with the type to be overriden by slot_usage */
    items: SearchResult[],
    /** Collection of facet field responses with the field values and counts */
    facet_fields?: {[index: FacetFieldLabel]: FacetField },
    /** Collection of facet query responses with the query string values and counts */
    facet_queries?: {[index: FacetValueLabel]: FacetValue },
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
    facet_values?: {[index: FacetValueLabel]: FacetValue },
};
/**
 * A data class to hold the necessary information to produce association type counts for given  entities with appropriate directional labels
 */
export interface AssociationTypeMapping {
    association_type?: string,
    /** A label to describe the subjects of the association type as a whole for use in the UI */
    subject_label?: string,
    /** A label to describe the objects of the association type as a whole for use in the UI */
    object_label?: string,
    /** Whether the association type is symmetric, meaning that the subject and object labels should be interchangeable */
    symmetric: boolean,
    /** The biolink categories to use in queries for this association type, assuming OR semantics */
    category?: string[],
    /** The biolink predicate to use in queries for this association type, assuming OR semantics */
    predicate: string[],
};

export interface AssociationCount extends FacetValue {
    association_type?: string,
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

