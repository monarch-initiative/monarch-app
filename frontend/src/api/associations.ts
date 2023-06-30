import { monarch, request } from "@/api";
import type { AssociationTableResults } from "@/api/model";

/** get associations between a node and a category */
export const getAssociations = async (
  nodeId = "",
  associationCategory = "",
  offset = 0,
  limit = 10
) => {
  /** make query params */
  const params = {
    offset,
    limit,
  };

  /** make query */
  const url = `${monarch}/entity/${nodeId}/${associationCategory}`;
  const response = await request<AssociationTableResults>(url, params);

  const transformedResponse = {
    ...response,
    items: response.items.map((association) => {
      const subject = {
        id: association.subject,
        name: association.subject_label || "",
        category: association.subject_category?.[0] || "",
      };
      const object = {
        id: association.object,
        name: association.object_label || "",
        category: association.object_category?.[0] || "",
      };
      const flip = association.direction !== "outgoing";
      return {
        ...association,
        this_node: flip ? object : subject,
        other_node: flip ? subject : object,
      };
    }),
  };

  return transformedResponse;
};

/** get top few associations */
export const getTopAssociations = async (
  nodeId = "",
  associationCategory = ""
) => await getAssociations(nodeId, associationCategory, 0, 5);
