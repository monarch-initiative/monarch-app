import { biolink, request } from "./";
import type { Filters, Query } from "./facets";
import { facetsToFilters, queryToParams } from "./facets";

/** Remove any special characters that would screw up backend search */
const encode = (string: string) => string.replaceAll(/[^a-zA-Z0-9]/g, " ");

/** Search results (from backend) */
type _SearchResults = {
  numFound: number;
  docs: {
    id: string;
    category?: string[];
    equivalent_curie?: string[];
    definition?: string[];
    label?: string[];
    score?: number;
    prefix?: string;
    taxon?: string;
    taxon_label?: string;
  }[];
  facet_counts: Record<string, Record<string, number>>;
  highlighting: Record<
    string,
    {
      highlight?: string;
    }
  >;
};

/** Search for node with text and filters */
export const getSearchResults = async (
  search = "",
  availableFilters: Query = {},
  activeFilters: Query = {},
  start = 0
): Promise<SearchResults> => {
  const empty = { count: 0, results: [], facets: {} };

  /** If nothing searched, return empty */
  if (!search.trim()) return empty;

  /** Other params */
  const params = {
    ...(await queryToParams(availableFilters, activeFilters)),
    boost_q: [
      "category:disease^5",
      "category:phenotype^5",
      "category:gene^0",
      "category:genotype^-10",
      "category:variant^-35",
    ],
    prefix: "-OMIA",
    min_match: "67%",
    rows: 10,
    start,
  };

  /** Make query */
  const url = `${biolink}/search/entity/${encode(search)}`;
  const response = await request<_SearchResults>(url, params);
  const {
    numFound: count = 0,
    docs = [],
    facet_counts = {},
    highlighting = {},
  } = response;

  /** Convert into desired result format */
  const results = docs.map((doc) => ({
    id: doc.id || "",
    name: (doc.label || [])[0] || "",
    altIds: doc.equivalent_curie || [],
    altNames: (doc.label || []).slice(1),
    category: (doc.category || [])[0] || "unknown",
    description: (doc.definition || [])[0] || "",
    score: doc.score || 0,
    prefix: doc.prefix || "",
    highlight: highlighting[doc.id].highlight,
    taxon:
      doc.taxon || doc.taxon_label
        ? {
            id: doc.taxon || "",
            name: doc.taxon_label || "",
          }
        : undefined,
  }));

  /** Empty error status */
  if (!results.length) return empty;

  /** Get facets for select options */
  const facets = facetsToFilters(facet_counts);

  return { count, results, facets };
};

/** Search results (for frontend) */
export type SearchResults = {
  count: number;
  results: {
    id: string;
    name?: string;
    altIds?: string[];
    altNames?: string[];
    category?: string;
    description?: string;
    score?: number;
    prefix?: string;
    highlight?: string;
    taxon?: {
      id: string;
      name: string;
    };
  }[];
  facets: Filters;
};

/** Autocomplete results (from backend) */
type _Autocomplete = {
  docs: [
    {
      match?: string;
      highlight?: string;
    }
  ];
};

/** Search for quick autocomplete matches to query string */
export const getAutocompleteResults = async (
  search = ""
): Promise<Autocomplete> => {
  const url = `${biolink}/search/entity/autocomplete/${encode(search)}`;
  const response = await request<_Autocomplete>(url);

  /** Transform into desired format */
  return response.docs.map((result) => ({
    name: result.match || "",
    highlight: result.highlight || "",
  }));
};

/** Autocomplete results (for frontend) */
type Autocomplete = {
  name: string;
  highlight: string;
}[];
