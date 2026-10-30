import { orderBy, pick, sortBy, uniqBy } from "lodash";
import type {
  AssociationResults,
  SemsimSearchResult,
  TermSetPairwiseSimilarity,
} from "@/api/model";
import type { Options, OptionsFunc } from "@/components/AppSelectTags.vue";
import type { Phenogrid } from "@/components/ThePhenogrid.vue";
import { stringify } from "@/util/object";
import { apiUrl, request } from "./";
import { getAutocomplete } from "./search";

/**
 * Hidden A/B switch: a `?engine=ducksim|semsimian` param in the page URL routes
 * all semsim API calls to that backend (default semsimian). Lets us compare
 * engines in place. The backend exposes this as a hidden `engine` query param
 * on the semsim endpoints.
 */
const engineParam = (): { engine?: string } => {
  const engine = new URLSearchParams(window.location.search).get("engine");
  return engine ? { engine } : {};
};

/** similarity metrics available for comparison */
export const metricOptions = [
  { id: "ancestor_information_content", label: "Ancestor Information Content" },
  { id: "jaccard_similarity", label: "Jaccard Similarity" },
  { id: "phenodigm_score", label: "Phenodigm Score" },
];

/**
 * How per-phenotype best matches are averaged into a score. In a search the
 * subject is each result and the object is the query.
 */
export const directionalityOptions = [
  { id: "bidirectional", label: "Both directions (default)" },
  {
    id: "object_to_subject",
    label: "How much of the query each result covers",
  },
  {
    id: "subject_to_object",
    label: "How much of each result the query covers",
  },
];

/** which entities a search scores */
export const searchModeOptions = [
  { id: "hybrid", label: "Prefilter by overlap (default)" },
  { id: "full", label: "Score every entity" },
];

/** where phenotype information content comes from */
export const informationContentOptions = [
  { id: "ontology", label: "Ontology structure (default)" },
  { id: "annotation", label: "How often phenotypes are annotated" },
];

/** how a search orders results with equal scores */
export const tieBreakOptions = [
  { id: "none", label: "By ID (default)" },
  { id: "frequency", label: "By phenotype frequency" },
];

/** search settings beyond the metric. omitted ones take the API defaults. */
export type SearchSettings = {
  directionality?: string;
  search_mode?: string;
  information_content?: string;
  tie_break?: string;
};

/** compare settings beyond the metric. omitted ones take the API defaults. */
export type CompareSettings = {
  directionality?: string;
  information_content?: string;
  /** annotation corpus, required when information_content is "annotation" */
  group?: string;
};

/** allowed values of each setting, the first being the API default */
const settingValues: Record<string, string[]> = {
  directionality: directionalityOptions.map(({ id }) => id),
  search_mode: searchModeOptions.map(({ id }) => id),
  information_content: informationContentOptions.map(({ id }) => id),
  tie_break: tieBreakOptions.map(({ id }) => id),
};

/**
 * keep only the settings that differ from the API defaults, so a request with
 * nothing changed is the same as one from before these settings existed.
 * unknown values are dropped too, the way an unknown metric falls back to the
 * default. the annotation corpus is kept only with annotation information
 * content, and only if it's a known group.
 */
export const cleanSettings = (
  settings: Record<string, unknown>,
): SearchSettings & CompareSettings => {
  const cleaned: Record<string, string> = {};
  for (const [field, values] of Object.entries(settingValues)) {
    const value = settings[field];
    if (typeof value === "string" && values.indexOf(value) > 0)
      cleaned[field] = value;
  }
  const group = settings.group;
  if (
    cleaned.information_content === "annotation" &&
    typeof group === "string" &&
    (groups as readonly string[]).includes(group)
  )
    cleaned.group = group;
  return cleaned;
};

/** search individual phenotypes or gene/disease phenotypes */
export const getPhenotypes = async (search = ""): ReturnType<OptionsFunc> => {
  /**
   * detect pasted list of phenotype ids. deliberately don't detect single id.
   * handle that with regular search.
   */
  const ids = search.split(/\s*,\s*/);
  if (ids.length >= 2)
    return {
      autoAccept: true,
      options: ids.map((id) => ({ id })),
    };

  /** otherwise perform string search for phenotypes/genes/diseases */
  const { items } = await getAutocomplete(search, true);

  /** convert into desired result format */
  return {
    options: items.map((item) => ({
      id: item.id,
      label: item.name,
      spreadOptions:
        /**
         * if gene/disease, provide function to get associated phenotypes upon
         * select
         */
        item.category?.startsWith("biolink:Pheno")
          ? undefined
          : async () => await getPhenotypeAssociations(item.id),
      icon: "category-" + item.category,
      info: item.in_taxon_label || "",
      infoItalic: !!item.in_taxon_label,
    })),
  };
};

/** get phenotypes associated with gene/disease */
const getPhenotypeAssociations = async (id = "") => {
  /** endpoint settings */
  const params = {
    subject: id,
    category: [
      "biolink:GeneToPhenotypicFeatureAssociation",
      "biolink:DiseaseToPhenotypicFeatureAssociation",
    ],
    limit: 500,
    direct: true,
  };

  /** make query */
  const url = `${apiUrl}/association`;
  const { items } = await request<AssociationResults>(url, params);

  /** convert into desired result format */
  return items.map((item) => ({
    id: item.object,
    name: item.object_label,
  })) satisfies Options;
};

/** compare a set of phenotypes to another set of phenotypes */
export const compareSetToSet = async (
  aPhenotypes: string[],
  bPhenotypes: string[],
  metric: string = "ancestor_information_content",
  settings: CompareSettings = {},
) => {
  /** make request options */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const body = {
    subjects: aPhenotypes,
    objects: bPhenotypes,
    metric: metric,
    ...settings,
  };
  const options = { method: "POST", headers, body: stringify(body) };

  /** make query */
  const url = `${apiUrl}/semsim/compare`;
  const response = await request<TermSetPairwiseSimilarity>(
    url,
    engineParam(),
    options,
  );

  /** map matches into nicer format */
  const mapMatches = (
    matches:
      | TermSetPairwiseSimilarity["subject_best_matches"]
      | TermSetPairwiseSimilarity["object_best_matches"],
  ) =>
    Object.values(matches || {}).map((match) => ({
      source: match.match_source,
      source_label: match.match_source_label,
      target: match.match_target,
      target_label: match.match_target_label,
      score: match.score,
      ...pick(match.similarity, [
        "ancestor_id",
        "ancestor_label",
        "ancestor_information_content",
        "jaccard_similarity",
        "phenodigm_score",
      ]),
    }));

  /** get high level data */
  let subjectMatches = mapMatches(response.subject_best_matches);
  let objectMatches = mapMatches(response.object_best_matches);
  subjectMatches = sortBy(subjectMatches, "score").reverse();
  objectMatches = sortBy(objectMatches, "score").reverse();

  /** find unmatched */
  const subjectUnmatched = Object.values(response.subject_termset || {}).filter(
    (term) => !(term.id in (response.subject_best_matches || {})),
  );
  const objectUnmatched = Object.values(response.object_termset || {}).filter(
    (term) => !(term.id in (response.object_best_matches || {})),
  );

  /** average best-match score per direction, unmatched phenotypes counting as 0 */
  const average = (matches: { score: number }[], unmatched: unknown[]) =>
    matches.length + unmatched.length
      ? matches.reduce((sum, match) => sum + match.score, 0) /
        (matches.length + unmatched.length)
      : 0;
  const subjectAverage = average(subjectMatches, subjectUnmatched);
  const objectAverage = average(objectMatches, objectUnmatched);

  return {
    subjectMatches,
    objectMatches,
    subjectUnmatched,
    objectUnmatched,
    subjectAverage,
    objectAverage,
  };
};

export type SetToSet = Awaited<ReturnType<typeof compareSetToSet>>;

/** types of groups */
export const groups = [
  "Human Diseases",
  "Human Genes",
  "Mouse Genes",
  "Rat Genes",
  "Zebrafish Genes",
  "C. Elegans Genes",
] as const;

export type Group = (typeof groups)[number];

type ObjectSet = { id?: string; label?: string; phenotypes: string[] };

export function processMulticompareResponse(
  response: SemsimSearchResult[],
  subjects: string[],
  objectSets: ObjectSet[],
) {
  /** make flat lists of rows/cols from subjects/objects */
  let cols: Phenogrid["cols"] = response.map((match, index) => ({
    id: match.subject.id || String(index),
    label: match.subject.name || `Set ${index + 1}`,
    total: 0,
  }));
  let rows: Phenogrid["cols"] = Object.values(
    response[0].similarity?.subject_termset || [],
  ).map((entry) => ({
    id: entry.id,
    label: entry.label,
    total: 0,
  }));

  /** preserve input sort order of rows/cols */
  rows = sortBy(rows, (row) => subjects.indexOf(row.id));
  cols = sortBy(cols, (col) =>
    objectSets.findIndex((object) => object.id === col.id),
  );

  /** now populate cells */
  const cells: Phenogrid["cells"] = {};

  /** start collecting unmatched phenotypes */
  let unmatched: Phenogrid["unmatched"] = [];

  for (const [index, col] of Object.entries(cols)) {
    for (const row of rows) {
      const match =
        response[+index]?.similarity?.subject_best_matches?.[row.id];

      col.total += match?.score || 0;
      row.total += match?.score || 0;

      cells[col.id + row.id] = {
        score: match?.score || 0,
        strength: 0,
        phenotype: match?.match_target || "",
        phenotypeLabel: match?.match_target_label || "",
        ...pick(match?.similarity, [
          "ancestor_id",
          "ancestor_label",
          "ancestor_information_content",
          "jaccard_similarity",
          "phenodigm_score",
        ]),
      };
    }
  }

  /** filter out unmatched phenotypes */
  cols = cols.filter((col) => {
    if (!col.total) unmatched.push({ ...col });
    return col.total;
  });
  rows = rows.filter((row) => {
    if (!row.total) unmatched.push({ ...row });
    return row.total;
  });

  /** deduplicate unmatched phenotypes */
  unmatched = uniqBy(unmatched, "id");

  /** normalize cell scores to 0-1 */
  const scores = Object.values(cells)
    .map((value) => value.score)
    .filter(Boolean);
  const min = Math.min(...scores);
  const max = Math.max(...scores);

  Object.values(cells).forEach(
    (value) =>
      (value.strength =
        max - min === 0 ? 0.5 : (value.score - min) / (max - min || 0)),
  );
  const phenogrid = { cols, rows, cells, unmatched } satisfies Phenogrid;

  return { phenogrid };
}

/** compare a set of phenotypes to several other sets of phenotypes */
export const compareSetToSets = async (
  subjects: string[],
  objectSets: ObjectSet[],
  metric?: string,
  settings: CompareSettings = {},
) => {
  /** fill in missing object set fields */
  objectSets.forEach((set, index) => {
    set.id ??= String(index);
    set.label ??= `Set ${index + 1}`;
  });

  /** make request */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const body = { subjects, object_sets: objectSets, metric, ...settings };
  const options = { method: "POST", headers, body: stringify(body) };

  /** make query */
  const url = `${apiUrl}/semsim/multicompare`;
  const response = await request<SemsimSearchResult[]>(
    url,
    engineParam(),
    options,
  );
  return processMulticompareResponse(response, subjects, objectSets);
};

/** compare a set of phenotypes to a group of phenotypes */
export const compareSetToGroup = async (
  phenotypes: string[],
  group: (typeof groups)[number],
  metric: string = "ancestor_information_content",
  settings: SearchSettings = {},
) => {
  /** make request options */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const body = { termset: phenotypes, group: group, metric, ...settings };
  const options = { method: "POST", headers, body: stringify(body) };

  /** make query */
  const url = `${apiUrl}/semsim/search`;
  const response = await request<SemsimSearchResult[]>(
    url,
    engineParam(),
    options,
  );

  /** get high level data */
  const matches = response.map((match) => ({
    subject: match.subject,
    score: match.score || 0,
    subjectToObjectScore: match.subject_to_object_score,
    objectToSubjectScore: match.object_to_subject_score,
  }));

  /**
   * highest score first. with a tie-break, ties keep the API's order, which
   * applies it. without one, ties keep the order this page always showed them
   * in (the API's, reversed).
   */
  const summary =
    settings.tie_break && settings.tie_break !== "none"
      ? orderBy(matches, "score", "desc")
      : sortBy(matches, "score").reverse();

  /** make flat lists of rows/cols from subjects/objects */
  let cols: Phenogrid["cols"] = response.map((match) => ({
    id: match.subject.id,
    label: match.subject.name,
    total: 0,
  }));
  let rows: Phenogrid["cols"] = Object.values(
    response[0].similarity?.object_termset || [],
  ).map((entry) => ({
    id: entry.id,
    label: entry.label,
    total: 0,
  }));

  /** preserve input sort order of rows */
  rows = sortBy(rows, (row) => phenotypes.indexOf(row.id));

  /** make map of col/row id to cells */
  const cells: Phenogrid["cells"] = {};

  /** collect unmatched phenotypes */
  let unmatched: Phenogrid["unmatched"] = [];

  for (const col of cols) {
    for (const row of rows) {
      /** find match corresponding to col/row id */
      const match = response.find((entry) => entry.subject.id === col.id)
        ?.similarity?.object_best_matches?.[row.id];

      /** sum up row and col scores */
      col.total += match?.score || 0;
      row.total += match?.score || 0;

      /** assign cell */
      cells[col.id + row.id] = {
        score: match?.score || 0,
        strength: 0,
        phenotype: match?.match_target || "",
        phenotypeLabel: match?.match_target_label || "",
        frequency: match?.frequency,
        ...pick(match?.similarity, [
          "ancestor_id",
          "ancestor_label",
          "ancestor_information_content",
          "jaccard_similarity",
          "phenodigm_score",
        ]),
      };
    }
  }

  /** filter out unmatched phenotypes */
  cols = cols.filter((col) => {
    if (!col.total) unmatched.push({ ...col });
    return col.total;
  });
  rows = rows.filter((row) => {
    if (!row.total) unmatched.push({ ...row });
    return row.total;
  });

  /** deduplicate unmatched phenotypes */
  unmatched = uniqBy(unmatched, "id");

  /** normalize cell scores to 0-1 */
  const scores = Object.values(cells)
    .map((value) => value.score)
    .filter(Boolean);
  const min = Math.min(...scores);
  const max = Math.max(...scores);
  Object.values(cells).forEach(
    (value) =>
      (value.strength =
        max - min === 0 ? 0.5 : (value.score - min) / (max - min || 0)),
  );

  /** assemble all data needed for phenogrid */
  const phenogrid = { cols, rows, cells, unmatched } satisfies Phenogrid;

  return { summary, phenogrid };
};

export type SetToTaxon = Awaited<ReturnType<typeof compareSetToSet>>;
