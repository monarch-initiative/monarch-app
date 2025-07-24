import { apiUrl, request } from "@/api";
import type { AssociationTableResults } from "@/api/model";
import type { Sort } from "@/components/AppTable.vue";

/** get associations between a node and a category */
export const getAssociations = async (
  nodeId = "",
  associationCategory = "",
  offset = 0,
  limit = 10,
  traverseOrthologs = false,
  direct = "false",
  search?: string,
  sort: Sort = null,
) => {
  /** make query params */
  let sortBy = sort?.key;

  /**
   * Sorting by frequency_qualifier is a special case. Those terms are entities
   * like HP:0040280 ("Always present"), and are only one out of three ways to
   * represent the frequency of a phenotypic association. The other two are a
   * ratio and a percentage. To sort all three values at the same time, we have
   * a derived column in the index that unifies all of these representation
   * called `frequency_computed_sortable_float`.
   *
   * This replacement could be done on /any/ frequency key (has_percentage,
   * has_count, has_total), but for now, we only use frequency qualifier in the
   * table.
   *
   * This could end up being a bug if someone /actually/, /really/ wanted to
   * only sort by the frequency qualifier, and have the other two classes show
   * up as null.
   */
  if (sortBy === "frequency_qualifier") {
    sortBy = "frequency_computed_sortable_float";
  }

  const params = {
    offset,
    limit,
    query: search || "",
    traverse_orthologs: !!traverseOrthologs,
    direct: direct,
    sort: sort ? `${sortBy} ${sort.direction === "up" ? "asc" : "desc"}` : null,
  };

  /** make query */
  const url = `${apiUrl}/entity/${nodeId}/${associationCategory}`;
  const response = await request<AssociationTableResults>(url, params);

  return response;
};

/** max rows supported in single download */
export const maxDownload = 500;

/** get associations between a node and a category */
export const downloadAssociations = async (
  nodeId = "",
  associationCategory = "",
  traverseOrthologs = false,
  direct = "false",
  search?: string,
  sort: Sort = null,
) => {
  /** make query params */

  let sortBy = sort?.key;

  /** See comment in getAssociations() */
  if (sortBy === "frequency_qualifier") {
    sortBy = "frequency_computed_sortable_float";
  }

  const params = {
    limit: maxDownload,
    query: search || "",
    traverse_orthologs: !!traverseOrthologs,
    direct: direct,
    sort: sort ? `${sortBy} ${sort.direction === "up" ? "asc" : "desc"}` : null,
    download: true,
    format: "tsv",
  };

  /** make query */
  const url = `${apiUrl}/entity/${nodeId}/${associationCategory}`;
  await request(url, params, {}, "text", true);
};

/** get top few associations */
export const getTopAssociations = async (
  nodeId = "",
  associationCategory = "",
) => await getAssociations(nodeId, associationCategory, 0, 5);

/** Get direct association facet counts for a node */
export const getDirectAssociationFacetCounts = async (nodeId = "") => {
  const params = {
    entity: nodeId,
    direct: true,
    facet_fields: "category",
    compact: false,
    format: "json",
    limit: 0,
    offset: 0,
  };

  const url = `${apiUrl}/association`;
  const rawResponse = await request<any>(url, params);
  console.log("rawResponse", rawResponse);
  // 👇 Transform the nested structure into what the UI expects

  const categoryFacet = rawResponse.facet_fields?.find(
    (item: any) => item.label === "category",
  );
  console.log("categoryFacet", categoryFacet);
  return {
    facet_field: "category",
    facet_counts: categoryFacet?.facet_values || [],
  };
};
