import type { Node } from "@/api/model";
import { stringify } from "@/util/object";
import { apiUrl, request } from "./index";

/** annotations (from backend) */
export type _Annotations = {
  text: string;
  tokens?: {
    id: string;
    name: string;
    category: string;
  }[];
}[];

/** get annotations from full text */
export const annotateText = async (content = ""): Promise<Annotations> => {
  /** if nothing searched, return empty */
  if (!content.trim()) return [];

  /** request params */
  const params = {};

  /** make request options */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const options = {
    method: "POST",
    headers,
    body: stringify({ content }),
  };

  /** make query */
  const url = `${apiUrl}/annotate`;
  const response = await request<_Annotations>(url, params, options);

  const transformedResponse = response.map((item) => ({
    ...item,
    tokens: item.tokens || [],
  }));

  return transformedResponse;
};

/** annotations (for frontend) */
export type Annotations = {
  text: string;
  tokens: Partial<Node>[];
}[];
