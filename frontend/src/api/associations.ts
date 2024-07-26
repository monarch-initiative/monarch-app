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
  const params = {
    offset,
    limit,
    query: search || "",
    traverse_orthologs: !!traverseOrthologs,
    direct: direct,
    sort: sort
      ? `${sort.key} ${sort.direction === "up" ? "asc" : "desc"}`
      : null,
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
  const params = {
    limit: maxDownload,
    query: search || "",
    traverse_orthologs: !!traverseOrthologs,
    direct: direct,
    sort: sort
      ? `${sort.key} ${sort.direction === "up" ? "asc" : "desc"}`
      : null,
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
