import type { SearchResults } from "@/api/model";
import { monarch, request } from "./index";

export type Filters = { [key: string]: string[] };

export const getSearch = async (
  q: string,
  offset?: number,
  limit?: number,
  filters?: Filters
) => {
  const url = `${monarch}/search`;
  const response = await request<SearchResults>(url, {
    q,
    offset,
    limit,
    ...filters,
  });
  return response;
};

export const getAutocomplete = async (q: string) => {
  const url = `${monarch}/autocomplete`;
  const response = await request<SearchResults>(url, { q });
  return response;
};
