export type NodeId = string;
export type TaxonId = string;
export type AssociationCountId = string;
export type AssociationId = string;
export type EntityId = string;
export type HistoPhenoId = string;
export type SearchResultId = string;
export type FacetValueLabel = string;
export type FacetFieldLabel = string;

export type Entity = {
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
};

export type Node = Entity & {
  taxon?: Taxon;
  inheritance?: Entity;
  association_counts?: { [index: AssociationCountId]: AssociationCount };
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
};

export type Taxon = {
  id?: string;
  label?: string;
};

export type AssociationCount = FacetValue & {
  id?: string;
  label?: string;
  /** number of items a this facet value */
  count?: number;
};

export type NodeHierarchy = {
  super_classes?: Entity[];
  equivalent_classes?: Entity[];
  sub_classes?: Entity[];
};

export type Association = {
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
};

export type AssociationResults = Results & {
  /** A collection of items, with the type to be overriden by slot_usage */
  items?: Association[];
  limit?: number;
  offset?: number;
  total?: number;
};

export type EntityResults = Results & {
  /** A collection of items, with the type to be overriden by slot_usage */
  items?: Entity[];
  limit?: number;
  offset?: number;
  total?: number;
};

export type HistoPheno = {
  id?: string;
  /** A collection of items, with the type to be overriden by slot_usage */
  items?: AssociationCount[];
};

export type Results = {
  limit?: number;
  offset?: number;
  total?: number;
};

export type SearchResult = Entity & {
  /** matching text snippet containing html tags */
  highlight?: string;
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
};

export type SearchResults = Results & {
  /** A collection of items, with the type to be overriden by slot_usage */
  items?: SearchResult[];
  facet_fields?: { [index: FacetFieldLabel]: FacetField };
  facet_queries?: { [index: FacetValueLabel]: FacetValue };
  limit?: number;
  offset?: number;
  total?: number;
};

export type FacetValue = {
  label?: string;
  /** number of items a this facet value */
  count?: number;
};

export type FacetField = {
  label?: string;
  facet_values?: { [index: FacetValueLabel]: FacetValue };
};
