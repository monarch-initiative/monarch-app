export const ENTITY_MAP: Record<string, { id: string; label: string; to?: string; text?: string }> =
  {
    'Ehlers-Danlos syndrome': {
      id: 'MONDO:0020066',
      label: 'Ehlers-Danlos syndrome',
      to: 'disease-to-phenotype',
    },
    'Down syndrome': {
      id: 'MONDO:0008608',
      label: 'Down syndrome',
      to: 'disease-model',
    },
    'cystic fibrosis': {
      id: 'MONDO:0009061',
      label: 'Cystic fibrosis',
      to: 'variant-to-disease',
    },
    FBN1: {
      id: 'HGNC:3603',
      label: 'FBN1',
      to: 'gene-to-phenotype',
    },
  };

export const KG_TOOL_LINKS: {
  label: string;
  to: string;
  icon?: string;
  external?: boolean;
  tooltip?: string;
}[] = [
  {
    label: 'Phenotype Search',
    icon: 'tool-phenotype-search',
    to: '/search-phenotypes',
    tooltip: 'Start exploring genes and diseases based on phenotype similarity',
  },
  {
    label: 'Text Annotator',
    icon: 'text-annotator',
    to: '/text-annotator',
    tooltip: 'Paste or upload text to find references to Monarch Knowledge Graph entities',
  },
  {
    label: 'Neo4j',
    icon: 'neoj',
    to: 'https://neo4j.monarchinitiative.org/browser/',
    tooltip: 'Explore the Monarch Knowledge Graph directly in the Neo4j browser',
    external: true,
  },
  {
    label: 'Monarch R',
    icon: 'monarchr',
    to: 'https://monarch-initiative.github.io/monarchr/articles/monarchr',
    tooltip: 'Query and manipulate Monarch KG data in a tidy-inspired R interface',
    external: true,
  },
];

export const TOOL_LINKS: {
  label: string;
  to: string;
  icon?: string;
  external?: boolean;
  tooltip?: string;
}[] = [
  {
    label: 'Exomiser',
    icon: 'exomiser-logo-banner.png',
    to: '/tools/exomiser',
    tooltip: 'Explore and prioritize genetic variants',
    external: true,
  },
  {
    label: 'Phenopackets',
    icon: 'phenopackets-logo.png',
    to: '/tools/phenopackets',
    tooltip: 'Standard format for sharing phenotypic and clinical data',
    external: true,
  },
  {
    label: 'Mondo',
    icon: 'mondo-logo-banner.png',
    to: '/ontologies/mondo',
    tooltip: 'Standardized vocabulary for diseases across clinical and research resources',
    external: true,
  },
  {
    label: 'Knowledge Graph',
    icon: 'kg-banner',
    to: '#header',
    tooltip: 'Search and explore genes, diseases, phenotypes, and more',
    external: true,
  },
];
