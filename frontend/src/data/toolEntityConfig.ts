export const ENTITY_MAP: Record<
  string,
  { id: string; label: string; to?: string; text?: string }
> = {
  "Ehlers-Danlos syndrome": {
    id: "MONDO:0020066",
    label: "Ehlers-Danlos syndrome",
    to: "disease-to-phenotype",
  },
  "Down syndrome": {
    id: "MONDO:0008608",
    label: "Down syndrome",
    to: "disease-model",
  },
  "cystic fibrosis": {
    id: "MONDO:0009061",
    label: "Cystic fibrosis",
    to: "variant-to-disease",
  },
  FBN1: {
    id: "HGNC:3603",
    label: "FBN1",
    to: "gene-to-phenotype",
  },
};

export const TOOL_LINKS: {
  label: string;
  to: string;
  icon?: string;
  external?: boolean;
  tooltip?: string;
}[] = [
  {
    label: "Exomiser",
    icon: "exomiser-logo-banner.png",
    to: "/tools/exomiser",
    tooltip: "Explore and prioritize genetic variants",
    external: true,
  },
  {
    label: "Phenopackets",
    icon: "phenopackets-logo.png",
    to: "/tools/phenopackets",
    tooltip: "Standard format for sharing phenotypic and clinical data",
    external: true,
  },
  {
    label: "Mondo",
    icon: "mondo-logo-banner.png",
    to: "/ontologies/mondo",
    tooltip:
      "Standardized vocabulary for diseases across clinical and research resources",
    external: true,
  },
  {
    label: "Knowledge Graph",
    icon: "kg-banner",
    to: "#header",
    tooltip: "Search and explore genes, diseases, phenotypes, and more",
    external: true,
  },
];
