import { labelFor } from "@/util/typeConfig";
import { pluralize } from "./plural";

// ---------- Types ----------
export type Vars = {
  node?: string;
  label?: string;
  n?: number; // direct count
  all?: number; // all count
  diff?: number; // all - direct
  example?: string; // e.g., inferred subclass label
};

type Fmt = (v: Vars) => string;
type NodeCategoryId = "biolink:Disease" | "biolink:PhenotypicFeature"; // add more later
type AssocId =
  | "biolink:DiseaseToPhenotypicFeatureAssociation"
  | "biolink:GeneToPhenotypicFeatureAssociation"
  | "biolink:CausalGeneToDiseaseAssociation"
  | "biolink:CorrelatedGeneToDiseaseAssociation"
  | "biolink:GenotypeToDiseaseAssociation"
  | "biolink:VariantToDiseaseAssociation"
  | "biolink:GenotypeToPhenotypicFeatureAssociation"
  | "biolink:VariantToPhenotypicFeatureAssociation";

type TemplatesByAssoc = Partial<Record<AssocId, Fmt>>;
type TemplatesByNodeCategory = Partial<
  Record<NodeCategoryId, TemplatesByAssoc>
>;

// quoted example (no bold/italic), also collapses whitespace
const q = (s?: string) => (s ? `“${s.replace(/\s+/g, " ").trim()}”` : "");

// Keep the word only (strip any leading number that pluralize might add)
const pluralWord = (
  n: number | null | undefined,
  singular: string,
  plural: string,
) =>
  String(pluralize(n ?? 0, singular, plural)).replace(
    /^\s*[+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*/,
    "",
  );

const fmtCount = (n: number | null | undefined) => (n ?? 0).toLocaleString();

const DIRECT_TEMPLATES: TemplatesByNodeCategory = {
  // Existing copy for Disease nodes
  "biolink:Disease": {
    "biolink:DiseaseToPhenotypicFeatureAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "phenotype", "phenotypes")} directly associated with ${node}`,
    "biolink:GeneToPhenotypicFeatureAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "gene with phenotypes", "genes with phenotypes")} that are directly associated with ${node}`,
    "biolink:CausalGeneToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "causal gene", "causal genes")} that causes ${node}`,
    "biolink:CorrelatedGeneToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "correlated gene", "correlated genes")} for ${node}`,
    "biolink:GenotypeToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "genotype", "genotypes")} that model ${node}`,
    "biolink:VariantToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "variant", "variants")} directly associated with ${node}`,
  },

  // New copy for PhenotypicFeature nodes
  "biolink:PhenotypicFeature": {
    "biolink:DiseaseToPhenotypicFeatureAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "disease", "diseases")} directly associated with phenotypic feature ${node}`,
    "biolink:GeneToPhenotypicFeatureAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "gene", "genes")} associated with phenotypic feature ${node}`,
    "biolink:CausalGeneToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "causal gene", "causal genes")} for diseases that exhibit ${node}`,
    "biolink:CorrelatedGeneToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "correlated gene", "correlated genes")} for diseases that exhibit ${node}`,
    "biolink:GenotypeToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "genotype", "genotypes")} that model diseases exhibiting ${node}`,
    "biolink:VariantToDiseaseAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "variant", "variants")} for diseases that exhibit ${node}`,
    "biolink:GenotypeToPhenotypicFeatureAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "genotype", "genotypes")} associated with phenotypic feature ${node}`,
    "biolink:VariantToPhenotypicFeatureAssociation": ({ n, node }) =>
      `${fmtCount(n)} ${pluralWord(n, "variant", "variants")} associated with phenotypic feature  ${node}`,
  },
};

// default direct template (fallback)
const defaultDirect: Fmt = ({ n, node, label }) =>
  `${(n ?? 0).toLocaleString()} ${label} directly associated with ${node}`;

// ----- INFERRED (only shown when all > 0) -----
// If no direct, keep it short: “{all} … associated with …”
// If direct > 0, include both and the subclass example if you have one.

const INFERRED_TEMPLATES: TemplatesByNodeCategory = {
  // When the node is a Disease
  "biolink:Disease": {
    "biolink:DiseaseToPhenotypicFeatureAssociation": ({
      all,
      n,
      diff,
      node,
      example,
    }) =>
      (n ?? 0) > 0
        ? `${pluralize(n, "phenotype", "phenotypes")} directly associated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")} ${example ? ` such as ${q(example)}` : ""}`
        : `${fmtCount(all)} phenotypes associated with ${node}`,
    "biolink:GeneToPhenotypicFeatureAssociation": ({
      all,
      n,
      diff,
      node,
      example,
    }) =>
      (n ?? 0) > 0
        ? `Phenotypes of the ${pluralize(n, "gene", "genes")} that cause subclasses of ${node} such as ${q(example)}`
        : ` ${pluralize(all, "gene", "genes")} with phenotypes associated with ${node}`,
    "biolink:CausalGeneToDiseaseAssociation": ({
      all,
      n,
      diff,
      node,
      example,
    }) =>
      (n ?? 0) > 0
        ? ` ${pluralize(n, "gene", "genes")} that causes ${node} as well as ${pluralize(diff, "subclass", "subclasses")} such as  ${example ? ` (e.g., ${q(example)})` : ""}`
        : `${pluralize(all, "gene", "genes")} that cause subtypes of ${node} such as ${q(example)}`,
    "biolink:CorrelatedGeneToDiseaseAssociation": ({
      all,
      n,
      diff,
      node,
      example,
    }) =>
      (n ?? 0) > 0
        ? `  ${pluralize(n, "correlated gene", "correlated genes")} for ${node} as well as  ${pluralize(diff, "subclass", "subclasses")} such as ${example ? `${q(example)}` : ""}`
        : ` ${pluralize(all, "correlated gene", "correlated genes")} associated with ${node}`,
    "biolink:GenotypeToDiseaseAssociation": ({
      all,
      n,
      diff,
      node,
      example,
    }) =>
      (n ?? 0) > 0
        ? `${pluralize(n, "disease model", "disease models")} that are associated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")} such as ${example ? ` ${q(example)}` : ""}`
        : ` ${pluralize(all, "disease model", "disease models")} that are associated with ${node}`,
    "biolink:VariantToDiseaseAssociation": ({ all, n, diff, node, example }) =>
      (n ?? 0) > 0
        ? ` ${pluralize(n, "variant", "variants")} that are associated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")} such as ${example ? ` ${q(example)}` : ""}`
        : ` ${pluralize(all, "variant", "variants")} that are associated with ${node}`,
  },
  // When the node is a Phenotypic Feature
  "biolink:PhenotypicFeature": {
    "biolink:DiseaseToPhenotypicFeatureAssociation": ({
      all,
      n,
      diff,
      node,
      example,
    }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "disease", "diseases")} directly associated with phenotypic feature ${node} as well as ${pluralize(diff, "subclass", "subclasses")}${example ? ` such as ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "disease", "diseases")} associated with ${node}`,

    "biolink:GeneToPhenotypicFeatureAssociation": ({
      all,
      n,
      node,
      diff,
      example,
    }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "gene", "genes")} associated with the phenotypic feature ${node} as well as ${pluralize(diff, "subclass", "subclasses")}${example ? ` such as  ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "gene", "genes")} associated with phenotypic feature  ${node}`,

    "biolink:CausalGeneToDiseaseAssociation": ({
      all,
      n,
      node,
      diff,
      example,
    }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "causal gene", "causal genes")} for diseases that exhibit ${node}  as well as  ${pluralize(diff, "subclass", "subclasses")} ${example ? `  such as  ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "gene", "genes")} causing diseases that exhibit ${node}`,

    "biolink:CorrelatedGeneToDiseaseAssociation": ({
      all,
      n,
      node,
      example,
      diff,
    }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "correlated gene", "correlated genes")} for diseases that exhibit ${node} as well as  ${pluralize(diff, "subclass", "subclasses")} ${example ? ` such as  ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "correlated gene", "correlated genes")} associated with diseases exhibiting ${node}`,

    "biolink:GenotypeToDiseaseAssociation": ({
      all,
      n,
      node,
      example,
      diff,
    }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "genotype", "genotypes")} that model diseases exhibiting ${node} as well as  ${pluralize(diff, "subclass", "subclasses")}  ${example ? `  such as  ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "genotype", "genotypes")} in disease models exhibiting ${node}`,

    "biolink:VariantToDiseaseAssociation": ({ all, n, node, example, diff }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "variant", "variants")} for diseases that exhibit ${node} as well as  ${pluralize(diff, "subclass", "subclasses")}  ${example ? `  such as  ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "variant", "variants")} associated with diseases exhibiting ${node}`,
    "biolink:GenotypeToPhenotypicFeatureAssociation": ({
      all,
      n,
      node,
      example,
      diff,
    }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "genotype", "genotypes")} associated with phenotypic feature ${node} as well as  ${pluralize(diff, "subclass", "subclasses")}  ${example ? `  such as  ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "genotype", "genotypes")} associated with phenotypic feature ${node}`,
    "biolink:VariantToPhenotypicFeatureAssociation": ({
      all,
      n,
      node,
      example,
      diff,
    }) =>
      (n ?? 0) > 0
        ? `${fmtCount(n)} ${pluralWord(n, "variant", "variants")} associated with associated with phenotypic feature ${node} as well as  ${pluralize(diff, "subclass", "subclasses")}  ${example ? `  such as  ${q(example)}` : ""}`
        : `${fmtCount(all)} ${pluralWord(all, "variant", "variants")} associated with associated with phenotypic feature  ${node}`,
  },
};

// default inferred template (fallback)
const defaultInferred: Fmt = ({ all, n, diff, node, label, example }) =>
  (n ?? 0) > 0
    ? `${(n ?? 0).toLocaleString()} ${label} directly associated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")}  ${example ? ` such as ${q(example)}` : ""}`
    : `${(all ?? 0).toLocaleString()} ${label} associated with ${node}`;

export function formatDirectTooltip(
  categoryId: string,
  nodeCategory: string,
  vars: Vars,
): string | undefined {
  const directCount = vars.n ?? 0;
  if (!Number.isFinite(directCount) || directCount <= 0) return undefined;

  const nodeTemplates =
    DIRECT_TEMPLATES[
      nodeCategory as "biolink:Disease" | "biolink:PhenotypicFeature"
    ];

  const directTemplate =
    nodeTemplates?.[categoryId as AssocId] ?? defaultDirect;

  const label = vars.label ?? labelFor(categoryId);

  return directTemplate({ ...vars, label });
}

export function formatInferredTooltip(
  categoryId: string,
  nodeCategory: string,
  vars: Vars,
): string | undefined {
  const totalCount = vars.all ?? 0;
  if (!Number.isFinite(totalCount) || totalCount <= 0) return undefined;

  const nodeTemplates =
    INFERRED_TEMPLATES[
      nodeCategory as "biolink:Disease" | "biolink:PhenotypicFeature"
    ];

  const inferredTemplate =
    nodeTemplates?.[categoryId as AssocId] ?? defaultInferred;

  const label = vars.label ?? labelFor(categoryId);
  return inferredTemplate({ ...vars, label });
}
