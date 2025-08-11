export type UseField = "subject_label" | "object_label";
export type TypeCfg = { label: string; use: UseField };

export const TYPE_CONFIG: Record<string, TypeCfg> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": {
    label: "phenotypes",
    use: "subject_label",
  },
  "biolink:GeneToPhenotypicFeatureAssociation": {
    label: "Gene To Phenotypes",
    use: "subject_label",
  },
  "biolink:CausalGeneToDiseaseAssociation": {
    label: "Causal Genes",
    use: "object_label",
  },
  "biolink:CorrelatedGeneToDiseaseAssociation": {
    label: "Correlated Genes",
    use: "object_label",
  },
  "biolink:GenotypeToDiseaseAssociation": {
    label: "Genotype to Disease",
    use: "object_label",
  },
};

export const labelFor = (id: string, fallback = "phenotypes") =>
  TYPE_CONFIG[id]?.label ?? fallback;

export const fieldFor = (id: string, fallback: UseField = "subject_label") =>
  TYPE_CONFIG[id]?.use ?? fallback;
