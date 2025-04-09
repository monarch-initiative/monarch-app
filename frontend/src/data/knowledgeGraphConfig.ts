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
  external?: boolean;
}[] = [
  { label: "Phenotype Similarity Compare", to: "/kg/compare-phenotypes" },
  { label: "Phenotype Similarity Search", to: "/kg/search-phenotypes" },
  {
    label: "Monarch R",
    to: "https://monarch-initiative.github.io/monarchr/articles/monarchr",
    external: true,
  },
  {
    label: "Neo4j",
    to: "https://neo4j.monarchinitiative.org/browser/",
    external: true,
  },
  { label: "Text Annotator", to: "/kg/text-annotator" },
  {
    label: "Monarch Assistant",
    to: "https://github.com/monarch-initiative/monarch-assistant-cypher",
    external: true,
  },
  {
    label: "MonarchKG API",
    to: "https://api-v3.monarchinitiative.org/v3/docs",
    external: true,
  },
];
