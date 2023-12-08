import { stringify } from "@/util/object";
import { apiUrl, request } from "./index";

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
  const response = await request<Annotations>(url, params, options);

  return response;
};

/** annotations (for frontend) */
export type Annotations = {
  text: string;
  tokens?: {
    id: string;
    name: string;
    category: string;
  }[];
}[];
