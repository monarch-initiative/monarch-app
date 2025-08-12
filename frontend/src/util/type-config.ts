export type UseField = "subject" | "object";
export type TypeCfg = { label: string; side: UseField };

export const TYPE_CONFIG: Record<string, TypeCfg> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": {
    label: "phenotypes",
    side: "subject",
  },
  "biolink:GeneToPhenotypicFeatureAssociation": {
    label: "Gene To Phenotypes",
    side: "subject",
  },
  "biolink:CausalGeneToDiseaseAssociation": {
    label: "Causal Genes",
    side: "object",
  },
  "biolink:CorrelatedGeneToDiseaseAssociation": {
    label: "Correlated Genes",
    side: "object",
  },
  "biolink:GenotypeToDiseaseAssociation": {
    label: "Genotype to Disease",
    side: "object",
  },
};

export const labelFor = (id: string, fallback = "phenotypes") =>
  TYPE_CONFIG[id]?.label ?? fallback;

export const fieldFor = (id: string, fallback: UseField = "subject") =>
  TYPE_CONFIG[id]?.side ?? fallback;
