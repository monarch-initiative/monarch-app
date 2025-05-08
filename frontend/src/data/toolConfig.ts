export const TOOL_LINKS: {
  label: string;
  to: string;
  icon?: string;
  external?: boolean;
  tooltip?: string;
}[] = [
  {
    label: "Phenotype Search",
    icon: "tool-phenotype-search",
    to: "/search-phenotypes",
    tooltip: "Start exploring genes and diseases based on phenotype similarity",
  },
  {
    label: "Text Annotator",
    icon: "text-annotator",
    to: "/text-annotator",
    tooltip:
      "Paste or upload text to find references to Monarch Knowledge Graph entities",
  },
  {
    label: "Neo4j",
    icon: "neoj",
    to: "https://neo4j.monarchinitiative.org/browser/",
    tooltip:
      "Explore the Monarch Knowledge Graph directly in the Neo4j browser",
    external: true,
  },
  {
    label: "Monarch R",
    icon: "monarchr",
    to: "https://monarch-initiative.github.io/monarchr/articles/monarchr",
    tooltip:
      "Query and manipulate Monarch KG data in a tidy-inspired R interface",
    external: true,
  },
  {
    label: "Monarch Assistant",
    icon: "monarch-assistant",
    to: "https://github.com/monarch-initiative/monarch-assistant-cypher",
    tooltip:
      "Browse Cypher query code and graph tools for the Monarch Assistant on GitHub",
    external: true,
  },
  {
    label: "MonarchKG API",
    icon: "code",
    to: "https://api-v3.monarchinitiative.org/v3/docs",
    tooltip: "Access the interactive documentation for Monarch's API v3",
    external: true,
  },
];
