export type DownloadItem = {
  label: string;
  description?: string;
  url: string;
};

export const knowledgeGraphDownloads: DownloadItem[] = [
  {
    label: "KGX TSV",
    url: "http://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.tar.gz",
  },
  {
    label: "KGX JSON Lines",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.jsonl.tar.gz",
  },
  {
    label: "RDF Format",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.nt.gz",
  },
  {
    label: "Neo4j Dump",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.neo4j.dump",
  },
  {
    label: "DuckDB Database",
    url: " https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.duckdb.gz",
  },
];

export const derivedArtifacts: DownloadItem[] = [
  {
    label: "Phenio SQLite (semsql)",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/phenio.db.gz",
  },
  {
    label: "Denormalized Associations",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg-denormalized-edges.tsv.gz",
  },
  {
    label: "Solr Data",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/solr.tar.gz",
  },
];

export const tsvIndexLink =
  "https://data.monarchinitiative.org/monarch-kg/latest/tsv/index.html";
