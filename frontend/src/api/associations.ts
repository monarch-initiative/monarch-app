import { apiUrl, request } from "@/api";
import type { AssociationTableResults } from "@/api/model";
import type { Sort } from "@/components/AppTable.vue";

/** get associations between a node and a category */
export const getAssociations = async (
  nodeId = "",
  associationCategory = "",
  offset = 0,
  limit = 10,
  search?: string,
  sort: Sort = null,
  download?: "tsv" | "json",
) => {
  /** make query params */
  const params = {
    offset,
    limit,
    query: search || "",
    sort: sort
      ? `${sort.key} ${sort.direction === "up" ? "asc" : "desc"}`
      : null,
    ...(download && { download: true, format: download }),
  };

  /** make query */
  const url = `${apiUrl}/entity/${nodeId}/${associationCategory}`;
  const response = await request<AssociationTableResults>(url, params);

  return response;
};

/** get top few associations */
export const getTopAssociations = async (
  nodeId = "",
  associationCategory = "",
) => await getAssociations(nodeId, associationCategory, 0, 5);
