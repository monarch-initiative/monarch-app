import { labelFor } from "@/util/typeConfig";
import { pluralize } from "./plural";

export type Vars = {
  node?: string;
  label?: string;
  n?: number; // direct count
  all?: number; // all count
  diff?: number; // all - direct
  example?: string; // e.g., inferred subclass label
};

type Fmt = (v: Vars) => string;

// quoted example (no bold/italic), also collapses whitespace
const q = (s?: string) => (s ? `“${s.replace(/\s+/g, " ").trim()}”` : "");

// ----- DIRECT (only shown when n > 0) -----
const DIRECT: Record<string, Fmt> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": ({ n, node }) =>
    `${(n ?? 0).toLocaleString()} phenotypes directly associated with ${node}`,
  "biolink:GeneToPhenotypicFeatureAssociation": ({ n, node }) =>
    `${(n ?? 0).toLocaleString()} genes with phenotypes that are directly associated with ${node}`,
  "biolink:CausalGeneToDiseaseAssociation": ({ n, node }) =>
    `${(n ?? 0).toLocaleString()} ${pluralize(n, "causal gene", "causal genes")} for ${node}`,
  "biolink:CorrelatedGeneToDiseaseAssociation": ({ n, node }) =>
    `${(n ?? 0).toLocaleString()} correlated genes for ${node}`,
  "biolink:GenotypeToDiseaseAssociation": ({ n, node }) =>
    `${(n ?? 0).toLocaleString()} genotypes that model ${node}`,
  "biolink:VariantToDiseaseAssociation": ({ n, node }) =>
    `${(n ?? 0).toLocaleString()} directly associated variants for ${node}`,
};

// default direct template (fallback)
const defaultDirect: Fmt = ({ n, node, label }) =>
  `${(n ?? 0).toLocaleString()} ${label} directly associated with ${node}`;

// ----- INFERRED (only shown when all > 0) -----
// If no direct, keep it short: “{all} … associated with …”
// If direct > 0, include both and the subclass example if you have one.
const INFERRED: Record<string, Fmt> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": ({
    all,
    n,
    diff,
    node,
    example,
  }) =>
    (n ?? 0) > 0
      ? `${(n ?? 0).toLocaleString()} phenotypes directly associated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")} ${example ? ` such as ${q(example)}` : ""}`
      : `${(all ?? 0).toLocaleString()} phenotypes associated with ${node}`,
  "biolink:GeneToPhenotypicFeatureAssociation": ({
    all,
    n,
    diff,
    node,
    example,
  }) =>
    (n ?? 0) > 0
      ? `Phenotypes of the ${all?.toLocaleString()} genes that cause subclasses of ${node} such as ${q(example)}`
      : `${(all ?? 0).toLocaleString()} Genes with phenotypes associated with ${node}`,
  "biolink:CausalGeneToDiseaseAssociation": ({
    all,
    n,
    diff,
    node,
    example,
  }) =>
    (n ?? 0) > 0
      ? `${(n ?? 0).toLocaleString()} genes for ${node} as well as  ${(diff ?? 0).toLocaleString()} such as  ${example ? ` (e.g., ${q(example)})` : ""}`
      : `${(all ?? 0).toLocaleString()} genes that cause subtypes of ${node} such as ${q(example)}`,
  "biolink:CorrelatedGeneToDiseaseAssociation": ({
    all,
    n,
    diff,
    node,
    example,
  }) =>
    (n ?? 0) > 0
      ? `${(n ?? 0).toLocaleString()} correlated genes for ${node} as wells as  ${pluralize(diff, "subclass", "subclasses")} such as ${example ? ` such as ${q(example)}` : ""}`
      : `${(all ?? 0).toLocaleString()} correlated genes associated with ${node}`,
  "biolink:GenotypeToDiseaseAssociation": ({ all, n, diff, node, example }) =>
    (n ?? 0) > 0
      ? `${(n ?? 0).toLocaleString()} disease models that are assciated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")} such as ${example ? ` ${q(example)}` : ""}`
      : `${(all ?? 0).toLocaleString()} disease models that are assciated with ${node}`,
  "biolink:VariantToDiseaseAssociation": ({ all, n, diff, node, example }) =>
    (n ?? 0) > 0
      ? `${(n ?? 0).toLocaleString()} variants that are assciated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")} such as ${example ? ` ${q(example)}` : ""}`
      : `${(all ?? 0).toLocaleString()} variants that are assciated with ${node}`,
};

// default inferred template (fallback)
const defaultInferred: Fmt = ({ all, n, diff, node, label, example }) =>
  (n ?? 0) > 0
    ? `${(n ?? 0).toLocaleString()} ${label} directly associated with ${node} as well as ${pluralize(diff, "subclass", "subclasses")} such as ${example ? ` such as ${q(example)}` : ""}`
    : `${(all ?? 0).toLocaleString()} ${label} associated with ${node}`;

export function formatDirectTooltip(
  categoryId: string,
  v: Vars,
): string | undefined {
  const n = v.n ?? 0;
  if (!Number.isFinite(n) || n <= 0) return undefined; // hide when zero
  const f = DIRECT[categoryId] ?? defaultDirect;
  // ensure label fallback if a category isn’t in DIRECT
  return f({ ...v, label: v.label || labelFor(categoryId) });
}

export function formatInferredTooltip(
  categoryId: string,
  v: Vars,
): string | undefined {
  const all = v.all ?? 0;

  if (!Number.isFinite(all) || all <= 0) return undefined;
  const f = INFERRED[categoryId] ?? defaultInferred;
  return f({ ...v, label: v.label || labelFor(categoryId) });
}
