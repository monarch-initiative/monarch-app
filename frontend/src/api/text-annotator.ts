import { getCategoryLabel } from "./categories";
import { apiUrl, request } from "./index";

/** annotations (from backend) */
type _Annotations = {
  content: string;
  spans: {
    start: number;
    end: number;
    text: string;
    token: {
      id: string;
      category: string[];
      terms: string[];
    }[];
  }[];
};

/** get annotations from full text */
export const annotateText = async (content = ""): Promise<Annotations> => {
  /** if nothing searched, return empty */
  if (!content.trim()) return [];

  /** request params */
  // const params = { longest_only: true };
  const params = {};

  /** make request options */
  const headers = new Headers();
  headers.append(
    "Content-Type",
    "application/x-www-form-urlencoded;charset=UTF-8",
  );
  const body = "content=" + window.encodeURIComponent(content);
  const options = { method: "POST", headers, body };

  console.log(body)

  /** make query */
  // const url = `${biolink}/nlp/annotate/entities`;
  const url = `${apiUrl}/annotate`;
  const response = await request<_Annotations>(url, params, options);
  const { spans } = response;

  /** empty */
  if (!spans.length) return [];

  /** get ordered, de-duped list of string indices, including start and end */
  const indices: [number, number][] = [
    0,
    ...new Set(spans.map(({ start, end }) => [start, end]).flat()),
    content.length - 1,
  ]
    .sort((a, b) => a - b)
    .map((index, i, array) => [index, array[i + 1] || index]);

  /** convert into desired result format */
  const annotations: Annotations = [];
  for (const [start, end] of indices) {
    annotations.push({
      text: content.slice(start, end),
      tokens: spans
        .filter((span) => span.start === start && span.end === end)
        .map(({ token }) => token[0])
        .filter((token) => token)
        .map((token) => ({
          id: token.id,
          name: token.terms.join(", "),
          category: getCategoryLabel(token.category),
        })),
    });
  }

  return annotations;
};

/** annotations (for frontend) */
export type Annotations = {
  text: string;
  tokens: {
    id: string;
    name: string;
    category: string;
  }[];
}[];
