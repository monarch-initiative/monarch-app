import { monarch, request } from "@/api";
import type { AssociationTableResults } from "@/api/model";

/** get associations between a node and a category */
export const getAssociations = async (
  nodeId = "",
  associationCategory = "",
  offset = 0,
  limit = 10,
  search?: string
) => {
  /** make query params */
  const params = {
    offset,
    limit,
    query: search || "",
  };

  /** make query */
  const url = `${monarch}/entity/${nodeId}/${associationCategory}`;
  const response = await request<AssociationTableResults>(url, params);

  return response;
};

/** get top few associations */
export const getTopAssociations = async (
  nodeId = "",
  associationCategory = ""
) => await getAssociations(nodeId, associationCategory, 0, 5);
