// This file defines API calls to fetch knowledge source facets (primary and aggregator sources)
// from the Monarch Initiative association endpoint. It includes type definitions for the expected
// API response structure and returns normalized, display-ready results.

import { apiUrl, request } from "@/api";

/**
 * The API returns `facet_counts` containing `facet_fields` for knowledge
 * sources.
 */
export interface FacetAPIResponse {
  facet_fields: {
    label: string;
    facet_values: {
      label: string;
      count: number;
    }[];
  }[];
}

/** Normalized result type for a knowledge source facet. */
export type FacetResult = {
  id: string;
  label: string;
  count: number;
};

/**
 * Generic function to fetch facet counts for a given knowledge source facet
 * field.
 *
 * @param facetField - Field to query ("primary_knowledge_source" or
 *   "aggregator_knowledge_source").
 * @returns List of normalized facet results.
 */
export const getKnowledgeSourceFacets = async (
  facetField: "primary_knowledge_source" | "aggregator_knowledge_source",
): Promise<FacetResult[]> => {
  const url = `${apiUrl}/association`;

  const params = {
    direct: false,
    facet_fields: facetField,
    compact: false,
    format: "json",
    limit: 0,
    offset: 0,
  };

  const response = await request<FacetAPIResponse>(url, params);

  // Safely extract facet buckets from the response
  let buckets = response.facet_fields?.[0]?.facet_values || [];

  // Filter out 'infores:monarchinitiative' for aggregator sources,
  // since it appears by default on every edge.
  if (facetField === "aggregator_knowledge_source") {
    buckets = buckets.filter(
      (item) => item.label !== "infores:monarchinitiative",
    );
  }

  // Transform each bucket into a FacetResult with cleaned label
  return buckets.map((item) => ({
    id: item.label,
    label: item.label.replace("infores:", "").toUpperCase(),
    count: item.count,
  }));
};
