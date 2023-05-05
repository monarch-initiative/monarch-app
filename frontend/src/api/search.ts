import type { SearchResults } from "@/api/model";
import { monarch, request } from "./index";

/** search for entity */
export const getSearch = async (
  q: string,
  offset: number,
  limit: number
): Promise<SearchResults> => {
  const url = `${monarch}/search`;
  const response = await request<SearchResults>(url, { q, offset, limit });

  return response;
};

export const getAutocomplete = async (q: string): Promise<SearchResults> => {
  const url = `${monarch}/autocomplete`;
  const response = await request<SearchResults>(url, { q });

  return response;
};
