import { pick, uniqBy } from "lodash";
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
        item.category.startsWith("biolink:Pheno")
          ? undefined
          : async () => await getPhenotypeAssociations(item.id),
      highlight: item.highlight,
      icon: "category-" + item.category,
      info: item.in_taxon_label || "",
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
) => {
  /** make request options */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const body = { subjects: aPhenotypes, objects: bPhenotypes };
  const options = { method: "POST", headers, body: stringify(body) };

  /** make query */
  const url = `${apiUrl}/semsim/compare`;
  const response = await request<TermSetPairwiseSimilarity>(url, {}, options);

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
        "jaccard_similarity",
        "phenodigm_score",
      ]),
    }));

  /** get high level data */
  const subjectMatches = mapMatches(response.subject_best_matches);
  const objectMatches = mapMatches(response.object_best_matches);
  subjectMatches.sort((a, b) => b.score - a.score);
  objectMatches.sort((a, b) => b.score - a.score);

  /** find unmatched */
  const subjectUnmatched = Object.values(response.subject_termset || {}).filter(
    (term) => !(term.id in (response.subject_best_matches || {})),
  );
  const objectUnmatched = Object.values(response.object_termset || {}).filter(
    (term) => !(term.id in (response.object_best_matches || {})),
  );

  return { subjectMatches, objectMatches, subjectUnmatched, objectUnmatched };
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

/** compare a set of phenotypes to several other sets of phenotypes */
export const compareSetToSets = async (
  subjects: string[],
  objects: string[][],
) => {
  /** make request */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
//  const body = { subjects: subjects, objects: objects };
//  const options = { method: "GET", headers, body: stringify(body) };

  // TODO: this could be prettier
  let objectsString = "";
  for (let i = 0; i < objects.length; i++) {
    objectsString += "objects=" + objects[i].join(",") + "&";
  }

  /** make query */
  const url = `${apiUrl}/semsim/multicompare/${subjects.join(",")}?${objectsString}`;
  const response = await request<TermSetPairwiseSimilarity[]>(url, {});

  //convert TermSetPairwiseSimilarity[] into Phenogrid
  //make a list of labels like 'setN' for each entry in response
  let labels: string[] = [];
  for (let i = 0; i < response.length; i++) {
    labels.push("set" + i);
  }

  let cols: Phenogrid["cols"] = labels.map((label) => ({
    id: label,
    label: label,
    total: 0,
  }));

  let rows: Phenogrid["cols"] = Object.values(
      response[0].object_termset || [],
  ).map((entry) => ({
    id: entry.id,
    label: entry.label,
    total: 0,
  }));

  //now populate cells

}


/** compare a set of phenotypes to a group of phenotypes */
export const compareSetToGroup = async (
  phenotypes: string[],
  group: (typeof groups)[number],
) => {
  /** make request options */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  const body = { termset: phenotypes, group: group };
  const options = { method: "POST", headers, body: stringify(body) };

  /** make query */
  const url = `${apiUrl}/semsim/search`;
  const response = await request<SemsimSearchResult[]>(url, {}, options);

  /** get high level data */
  const summary = response.map((match) => ({
    subject: match.subject,
    score: match.score || 0,
  }));
  summary.sort((a, b) => b.score - a.score);

  /** turn objects into array of cols */
  let cols: Phenogrid["cols"] = response.map((match) => ({
    id: match.subject.id,
    label: match.subject.name,
    total: 0,
  }));
  /** turn subjects into array of rows */
  let rows: Phenogrid["cols"] = Object.values(
    response[0].similarity?.object_termset || [],
  ).map((entry) => ({
    id: entry.id,
    label: entry.label,
    total: 0,
  }));

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
        ...pick(match?.similarity, [
          "ancestor_id",
          "ancestor_label",
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
