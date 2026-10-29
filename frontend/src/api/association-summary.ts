import { apiUrl, request } from "@/api";

/** one facet value, with its label when the facet has a label field */
export type SummaryFacetValue = {
  value: string;
  count: number;
  label?: string | null;
};

/** one group_by bucket of an association summary */
export type AssociationSummaryGroup = {
  value: string;
  count: number;
  unique: Record<string, number>;
  stats: Record<string, { min?: string | null; max?: string | null }>;
  fields: Record<string, string | null>;
  facets: Record<string, SummaryFacetValue[]>;
};

/** facet-only summary of an entity's association section */
export type AssociationSummary = {
  total: number;
  group_by: string;
  group_total: number;
  offset: number;
  limit: number;
  unique: Record<string, number>;
  facets: Record<string, SummaryFacetValue[]>;
  groups: AssociationSummaryGroup[];
};

export type AssociationSummaryParams = {
  groupBy: string;
  uniqueFields?: string[];
  statFields?: string[];
  labelFields?: string[];
  facetFields?: string[];
  /** facet field → label field, e.g. { object: "object_label" } */
  facetLabels?: Record<string, string>;
  groupSort?: string;
  facetLimit?: number;
  direct?: boolean;
  filterQueries?: string[];
  offset?: number;
  limit?: number;
};

/** summarize a node's association section, grouped by one field */
export const getAssociationSummary = async (
  nodeId: string,
  sectionKey: string,
  params: AssociationSummaryParams,
) => {
  const url = `${apiUrl}/entity/${nodeId}/${sectionKey}/summary`;
  return await request<AssociationSummary>(url, {
    group_by: params.groupBy,
    unique_fields: params.uniqueFields,
    stat_fields: params.statFields,
    label_fields: params.labelFields,
    facet_fields: params.facetFields,
    facet_labels: Object.entries(params.facetLabels ?? {}).map(
      ([field, label]) => `${field}:${label}`,
    ),
    group_sort: params.groupSort,
    facet_limit: params.facetLimit,
    direct: params.direct,
    filter_queries: params.filterQueries,
    offset: params.offset,
    limit: params.limit,
  });
};

/** quote a value for use in a Solr filter query */
export const solrQuote = (value: string) =>
  `"${value.replace(/(["\\])/g, "\\$1")}"`;
