import { mapCategory } from "@/api/categories";
import type { SearchResults } from "@/api/model";
import { monarch, request } from "./index";

export type Filters = { [key: string]: string[] };

export const getSearchResults = async (
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

  const transformedResponse = {
    ...response,
    items: response.items.map((item) => ({
      ...item,
      category: mapCategory(item.category),
    })),
  };

  return transformedResponse;
};

export const getAutocompleteResults = async (q: string) => {
  const url = `${monarch}/autocomplete`;
  const response = await request<SearchResults>(url, { q });

  const transformedResponse = {
    ...response,
    items: response.items.map((item) => ({
      ...item,
      category: mapCategory(item.category),
    })),
  };

  return transformedResponse;
};
