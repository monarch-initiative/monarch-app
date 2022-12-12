export type NodeId = string
export type TaxonId = string
export type AssociationId = string
export type EntityId = string

export interface Node  extends Entity  {
    taxon?: Taxon,
    inheritance?: Entity,
    association_counts?: AssociationCount[],
    node_hierarchy?: NodeHierarchy,
    id?: string,
    category?: string,
    name?: string,
    description?: string,
    xref?: string,
    provided_by?: string,
    in_taxon?: string,
    source?: string,
    symbol?: string,
    type?: string,
    synonym?: string,
}

export interface Taxon  {
    id?: string,
    label?: string,
}

export interface AssociationCount  {
    label?: string,
    count?: number,
}

export interface NodeHierarchy  {
    super_classes?: Entity[],
    equivalent_classes?: Entity[],
    sub_classes?: Entity[],
}

export interface Association  {
    aggregator_knowledge_source?: string,
    id?: string,
    subject?: string,
    original_subject?: string,
    subject_namespace?: string,
    subject_category?: string,
    subject_closure?: string,
    subject_label?: string,
    subject_closure_label?: string,
    predicate?: string,
    object?: string,
    original_object?: string,
    object_namespace?: string,
    object_category?: string,
    object_closure?: string,
    object_label?: string,
    object_closure_label?: string,
    knowledge_source?: string,
    primary_knowledge_source?: string,
    category?: string,
    negated?: boolean,
    provided_by?: string,
    publications?: string,
    qualifiers?: string,
    frequency_qualifier?: string,
    has_evidence?: string,
    onset_qualifier?: string,
    sex_qualifier?: string,
    source?: string,
    stage_qualifier?: string,
    pathway?: string,
    relation?: string,
}

export interface AssociationResults  extends Results  {
    associations?: Association[],
    limit?: number,
    offset?: number,
    total?: number,
}

export interface Entity  {
    id?: string,
    category?: string,
    name?: string,
    description?: string,
    xref?: string,
    provided_by?: string,
    in_taxon?: string,
    source?: string,
    symbol?: string,
    type?: string,
    synonym?: string,
}

export interface EntityResults  extends Results  {
    entities?: Entity[],
    limit?: number,
    offset?: number,
    total?: number,
}

export interface Results  {
    limit?: number,
    offset?: number,
    total?: number,
}

