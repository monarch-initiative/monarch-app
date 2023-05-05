export type NodeId = string;
export type TaxonId = string;
export type AssociationId = string;
export type EntityId = string;
export type HistoPhenoId = string;
export type HistoBinId = string;
export type SearchResultId = string;
export type FacetValueLabel = string;
export type FacetFieldLabel = string;
export type AssociationCountLabel = string;

export interface Node extends Entity {
  taxon?: Taxon;
  inheritance?: Entity;
  association_counts?: AssociationCount[];
  node_hierarchy?: NodeHierarchy;
  id?: string;
  category?: string;
  name?: string;
  description?: string;
  xref?: string;
  provided_by?: string;
  in_taxon?: string;
  source?: string;
  symbol?: string;
  type?: string;
  synonym?: string;
}

export interface Taxon {
  id?: string;
  label?: string;
}

export interface NodeHierarchy {
  super_classes?: Entity[];
  equivalent_classes?: Entity[];
  sub_classes?: Entity[];
}

export interface Association {
  aggregator_knowledge_source?: string;
  id?: string;
  subject?: string;
  original_subject?: string;
  subject_namespace?: string;
  subject_category?: string;
  subject_closure?: string;
  subject_label?: string;
  subject_closure_label?: string;
  predicate?: string;
  object?: string;
  original_object?: string;
  object_namespace?: string;
  object_category?: string;
  object_closure?: string;
  object_label?: string;
  object_closure_label?: string;
  primary_knowledge_source?: string;
  category?: string;
  negated?: boolean;
  provided_by?: string;
  publications?: string;
  qualifiers?: string;
  frequency_qualifier?: string;
  has_evidence?: string;
  onset_qualifier?: string;
  sex_qualifier?: string;
  source?: string;
  stage_qualifier?: string;
  pathway?: string;
  relation?: string;
}

export interface AssociationResults extends Results {
  /** A collection of items, with the type to be overriden by slot_usage */ items?: Association[];
  limit?: number;
  offset?: number;
  total?: number;
}

export interface Entity {
  id?: string;
  category?: string;
  name?: string;
  description?: string;
  xref?: string;
  provided_by?: string;
  in_taxon?: string;
  source?: string;
  symbol?: string;
  type?: string;
  synonym?: string;
}

export interface EntityResults extends Results {
  /** A collection of items, with the type to be overriden by slot_usage */ items?: Entity[];
  limit?: number;
  offset?: number;
  total?: number;
}

export interface HistoPheno {
  id?: string;
  /** A collection of items, with the type to be overriden by slot_usage */ items?: HistoBin[];
}

export interface HistoBin extends FacetValue {
  id?: string;
  label?: string;
  /** number of items a this facet value */ count?: number;
}

export interface Results {
  limit?: number;
  offset?: number;
  total?: number;
}

export interface SearchResult extends Entity {
  /** matching text snippet containing html tags */ highlight?: string;
  score?: number;
  id?: string;
  category?: string;
  name?: string;
  description?: string;
  xref?: string;
  provided_by?: string;
  in_taxon?: string;
  source?: string;
  symbol?: string;
  type?: string;
  synonym?: string;
}

export interface SearchResults extends Results {
  /** A collection of items, with the type to be overriden by slot_usage */ items?: SearchResult[];
  facet_fields?: { [index: FacetFieldLabel]: FacetField };
  facet_queries?: { [index: FacetValueLabel]: FacetValue };
  limit?: number;
  offset?: number;
  total?: number;
}

export interface FacetValue {
  label?: string;
  /** number of items a this facet value */ count?: number;
}

export interface FacetField {
  label?: string;
  facet_values?: { [index: FacetValueLabel]: FacetValue };
}
/**
 * A data class to hold the necessary information to produce association type
 * counts for given entities with appropriate directional labels
 */
export interface AssociationTypeMapping {
  association_type?: string;
  /**
   * A label to describe the subjects of the association type as a whole for use
   * in the UI
   */ subject_label?: string;
  /**
   * A label to describe the objects of the association type as a whole for use
   * in the UI
   */ object_label?: string;
  /**
   * The biolink categories to use in queries for this association type,
   * assuming OR semantics
   */ category?: string;
  /**
   * The biolink predicate to use in queries for this association type, assuming
   * OR semantics
   */ predicate?: string;
}

export interface AssociationCount extends FacetValue {
  association_type?: string;
  label?: string;
  /** number of items a this facet value */ count?: number;
}
/** Container class for a list of association counts */
export interface AssociationCountList {
  /** A collection of items, with the type to be overriden by slot_usage */ items?: AssociationCount[];
}
