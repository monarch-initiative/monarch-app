import type {
  AssociationResults,
  TermSetPairwiseSimilarity,
} from "@/api/model";
import type { Options, OptionsFunc } from "@/components/AppSelectTags.vue";
import { stringify } from "@/util/object";
import { biolink, monarch, request } from "./";
import { getSearch } from "./search";

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
      message: ids.every((id) => id.startsWith("HP:"))
        ? ""
        : 'One or more pasted IDs were not valid HPO phenotype IDs (starting with "HP:")',
    };

  /** otherwise perform string search for phenotypes/genes/diseases */
  const { items } = await getSearch(search, 0, 20, {
    category: [
      "biolink:PhenotypicFeature",
      "biolink:PhenotypicQuality",
      "biolink:Gene",
      "biolink:Disease",
    ],
  });

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
      info: item.in_taxon || "",
    })),
  };
};

/** get phenotypes associated with gene/disease */
const getPhenotypeAssociations = async (id = ""): Promise<Options> => {
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
  const url = `${monarch}/association`;
  const { items } = await request<AssociationResults>(url, params);

  /** convert into desired result format */
  return items.map((item) => ({
    id: item.object,
    name: item.object_label,
  }));
};

/** results of phenotype comparison (from backend) */
type _Comparison = {
  matches: {
    id: string;
    label: string;
    type: string;
    taxon?: {
      id?: string;
      label?: string;
    };
    rank: string;
    score: number;
    significance: string;
  }[];
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
  const url = `${monarch}/semsim/compare`;
  const response = await request<TermSetPairwiseSimilarity>(url, {}, options);

  const matches = Object.values(response.subject_best_matches || {}).map(
    (match) => ({
      source: match.match_source,
      source_label: match.match_source_label,
      target: match.match_target,
      target_label: match.match_target_label,
      score: match.score,
    }),
  );

  matches.sort((a, b) => b.score - a.score);

  return matches;
};

/** compare a set of phenotypes to a gene or disease taxon id */
export const compareSetToTaxon = async (
  phenotypes: string[],
  taxon: string,
): Promise<Comparison> => {
  /** endpoint settings */
  const params = {
    id: phenotypes,
    taxon: taxon,
  };

  /** make query */
  const url = `${biolink}/sim/search`;
  const response = await request<_Comparison>(url, params);

  return mapMatches(response);
};

/** convert comparison matches into desired result format */
const mapMatches = (response: _Comparison) => {
  const matches = response.matches.map((match) => ({
    id: match.id,
    name: match.label,
    score: match.score,
    category: match.type || "phenotype",
    taxon: match.taxon?.label || "",
  }));
  const minScore = Math.min(...matches.map(({ score }) => score));
  const maxScore = Math.max(...matches.map(({ score }) => score));

  return { matches, minScore, maxScore };
};

/** results of phenotype comparison (for frontend) */
export type Comparison = {
  matches: {
    id: string;
    name: string;
    score: number;
    category: string;
    taxon: string;
  }[];
  minScore?: number;
  maxScore?: number;
};
