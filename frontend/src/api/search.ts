import type { SearchResults } from "@/api/model";
import { apiUrl, request } from "./index";

export type Filters = { [key: string]: string[] };

export const getSearch = async (
  q: string,
  offset?: number,
  limit?: number,
  filters?: Filters,
) => {
  const url = `${apiUrl}/search`;
  const response = await request<SearchResults>(url, {
    q,
    offset,
    limit,
    ...filters,
  });

  return response;
};

export const getAutocomplete = async (q: string, semsim: boolean = false) => {
  const url = semsim
    ? `${apiUrl}/semsim/autocomplete`
    : `${apiUrl}/autocomplete`;

  const response = await request<SearchResults>(url, { q });

  const transformedResponse = {
    ...response,
    items: response.items.slice(0, 20),
  };

  return transformedResponse;
};
