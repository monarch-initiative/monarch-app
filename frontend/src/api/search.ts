import type { SearchResults } from "@/api/model";
import { monarch, request } from "./index";

export const getSearch = async (q: string): Promise<SearchResults> => {
  /** make query */
  /* TODO: add faceting support */
  const url = `${monarch}/search?q=${q}`;
  const response: SearchResults = await request<SearchResults>(url);

  return response;
};

export const getAutocomplete = async (q: string): Promise<SearchResults> => {
  /** make query */
  const url = `${monarch}/autocomplete?q=${q}`;
  const response: SearchResults = await request<SearchResults>(url);

  return response;
};
