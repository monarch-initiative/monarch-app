import { startCase } from "lodash";

/** from list of categories, get single category to label/display */
export const mapCategory = (category: string[] = []): string =>
  category[0]?.replace("biolink:", "")?.toLowerCase() || "unknown";

/**
 * from a category name, get its pluralized form, for querying association
 * endpoints
 */
export const getAssociationEndpoint = (category = ""): string => {
  /** special */
  if (category === "anatomy") return "expression/anatomy";
  if (category === "ortholog-phenotype") return "ortholog/phenotypes";
  if (category === "ortholog-disease") return "ortholog/diseases";

  /** causal/correlated */
  if (category === "causal-disease" || category === "correlated-disease")
    return "diseases";
  if (category === "causal-gene" || category === "correlated-gene")
    return "genes";

  /** non-pluralized */
  if (category === "function") return category;

  /** regular pluralized (most cases) */
  return `${category}s`;
};

/** from a category name, get how it should be labeled when viewing associations */
export const getAssociationLabel = (category = ""): string => {
  if (category === "anatomy") return "Anatomies";

  if (category === "ortholog-phenotype") return "Ortholog Phenotypes";
  if (category === "ortholog-disease") return "Ortholog Diseases";

  if (category === "causal-disease") return "Causal Diseases";
  if (category === "correlated-disease") return "Correlated Diseases";
  if (category === "causal-gene") return "Causal Genes";
  if (category === "correlated-gene") return "Correlated Genes";

  /** regular pluralized (most cases) */
  return `${startCase(category)}s`;
};

/**
 * categories that app supports. keep in specific order of "importance", used
 * for sorting.
 */
export const categories = [
  "phenotype",
  "disease",
  "gene",
  "variant",
  "genotype",
  "anatomy",
  "pathway",
  "homolog",
  "interaction",
  "publication",
  "model",
  "case",
  "cell-line",
  "function",
  "ortholog-disease",
  "ortholog-phenotype",
  "causal-disease",
  "correlated-disease",
  "causal-gene",
  "correlated-gene",
];
