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
  color?: string;
}[] = [
  {
    label: "Phenotype Similarity Compare",
    icon: "tool-resource-hpo",
    to: "/kg/compare-phenotypes",
  },
  {
    label: "Phenotype Similarity Search",
    icon: "tool-phenotype-search",

    to: "/kg/search-phenotypes",
  },
  { label: "Text Annotator", icon: "text-annotator", to: "/kg/text-annotator" },
  {
    label: "Neo4j",
    icon: "neoj",
    to: "https://neo4j.monarchinitiative.org/browser/",
    external: true,
  },
  {
    label: "Monarch R",
    icon: "diagram-project",
    to: "https://monarch-initiative.github.io/monarchr/articles/monarchr",
    external: true,
    color: "#FFB470",
  },
  {
    label: "Monarch Assistant",
    icon: "person-running",
    to: "https://github.com/monarch-initiative/monarch-assistant-cypher",
    external: true,
  },
  {
    label: "MonarchKG API",
    icon: "code",
    to: "https://api-v3.monarchinitiative.org/v3/docs",
    external: true,
  },
];
