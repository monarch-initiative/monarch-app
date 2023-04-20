import { monarch, request } from "./index";
import type { Node } from "./model";

export const getEntity = async (id: string): Promise<Node> => {
  /** make query */
  const url = `${monarch}/entity/${id}`;
  const response: Node = await request<Node>(url);

  return response;
};
