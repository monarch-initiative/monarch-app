import { groupBy, uniq } from "lodash";
import type { SearchResult, SearchResults } from "@/api/model";
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

type DedupedSearchResults = Omit<SearchResults, "items"> & {
  items: (SearchResult & { dupes: string[] })[];
};

export const getAutocomplete = async (q: string) => {
  const url = `${apiUrl}/autocomplete`;
  const response = await request<SearchResults>(url, { q });

  const transformedResponse: DedupedSearchResults = {
    ...response,
    items: Object.values(
      /** consolidate items */
      groupBy(
        response.items,
        /** by name, case insensitively */
        (item) => item.name.toLowerCase(),
      ),
    ).map((dupes) => ({
      ...dupes[0],
      /** keep list of duplicated names */
      /** de-dupe this list case sensitively */
      dupes: uniq(dupes.map((dupe) => dupe.name)),
    })),
  };

  return transformedResponse;
};
