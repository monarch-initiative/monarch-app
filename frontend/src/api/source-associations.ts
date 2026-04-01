import { apiUrl, request } from "@/api";
import type { AssociationResults } from "@/api/model";
import type { Sort } from "@/components/AppTable.vue";

/** get associations, optionally filtered by primary knowledge source */
export const getSourceAssociations = async (
  primaryKnowledgeSource?: string,
  offset = 0,
  limit = 20,
  facetFields?: string[],
  filterQueries?: string[],
  sort: Sort = null,
  search?: string,
) => {
  let sortBy = sort?.key;
  if (sortBy === "frequency_qualifier") {
    sortBy = "frequency_computed_sortable_float";
  }

  const params = {
    primary_knowledge_source: primaryKnowledgeSource || undefined,
    offset,
    limit,
    query: search || undefined,
    sort: sort
      ? `${sortBy} ${sort.direction === "up" ? "asc" : "desc"}`
      : undefined,
    facet_fields: facetFields,
    filter_queries: filterQueries,
    format: "json",
  };

  const url = `${apiUrl}/association`;
  const response = await request<AssociationResults>(url, params);
  return response;
};
