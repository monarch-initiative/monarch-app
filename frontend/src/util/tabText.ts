// src/util/tab-text.ts
import { labelFor } from "@/util/type-config";

type TabKind = "direct" | "inferred";
type Ctx = { label: string };
type Make = (ctx: Ctx) => string;
type Entry = { direct: Make; inferred: Make };

const OVERRIDES: Record<string, Entry> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": {
    direct: () => "Directly associated phenotypes",
    inferred: () => "Inferred associated phenotypes",
  },
  "biolink:GeneToPhenotypicFeatureAssociation": {
    direct: () => "Directly associated causal gene phenotypes",
    inferred: () => "Inferred associated causal gene phenotypes",
  },
  "biolink:CausalGeneToDiseaseAssociation": {
    direct: () => "Directly associated causal genes",
    inferred: () => "Inferred associated causal genes",
  },
  "biolink:CorrelatedGeneToDiseaseAssociation": {
    direct: () => "Directly associated correlated genes",
    inferred: () => "Inferred associated correlated genes",
  },
  "biolink:GenotypeToDiseaseAssociation": {
    direct: () => "Directly associated disease models",
    inferred: () => "Inferred associated disease models",
  },
};

const DEFAULTS: Entry = {
  direct: ({ label }) => `Directly associated ${label}`,
  inferred: ({ label }) => `Inferred associated ${label}`,
};

export function tabLabel(categoryId: string, kind: TabKind): string {
  const label = labelFor(categoryId);
  const entry = OVERRIDES[categoryId] ?? DEFAULTS;
  return entry[kind]({ label }).trim();
}
