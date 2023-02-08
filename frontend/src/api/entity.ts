import { Node } from "./model";
import { monarch, request } from "./index";

export const getEntity = async (id: string): Promise<Node> => {
  /** make query */
  const url = `${monarch}/entity/${id}`;
  const response: Node = await request<Node>(url);

  return response;
};
