import { biolink, request } from "./index";
import { mapCategory } from "./categories";

/** annotations (from backend) */
interface _Annotations {
  content: string;
  spans: Array<{
    start: number;
    end: number;
    text: string;
    token: Array<{
      id: string;
      category: Array<string>;
      terms: Array<string>;
    }>;
  }>;
}

/** get annotations from full text */
export const annotateText = async (content = ""): Promise<Annotations> => {
  /** if nothing searched, return empty */
  if (!content.trim()) return [];

  /** request params */
  const params = { longest_only: true };

  /** make request options */
  const headers = new Headers();
  headers.append(
    "Content-Type",
    "application/x-www-form-urlencoded;charset=UTF-8"
  );
  const body = "content=" + window.encodeURIComponent(content);
  const options = { method: "POST", headers, body };

  /** make query */
  const url = `${biolink}/nlp/annotate/entities`;
  const response = await request<_Annotations>(url, params, options);
  const { spans } = response;

  /** empty */
  if (!spans.length) return [];

  /** get ordered, de-duped list of string indices, including start and end */
  const indices: Array<[number, number]> = [
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
          category: mapCategory(token.category),
        })),
    });
  }

  return annotations;
};

/** annotations (for frontend) */
export type Annotations = Array<{
  text: string;
  tokens: Array<{
    id: string;
    name: string;
    category: string;
  }>;
}>;
