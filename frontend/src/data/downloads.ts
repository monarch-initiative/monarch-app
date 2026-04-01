/* eslint-disable max-len */
export type DownloadItem = {
  label: string;
  description?: string;
  url: string;
};

export const knowledgeGraphDownloads: DownloadItem[] = [
  {
    label: "KGX TSV",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.tar.gz",
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
    url: "https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.duckdb",
  },
];

export const associations: DownloadItem[] = [
  {
    label: "Causal gene to disease association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/causal_gene_to_disease_association.all.tsv.gz",
  },
  {
    label:
      "Chemical or drug or treatment to disease or phenotypic feature association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/chemical_or_drug_or_treatment_to_disease_or_phenotypic_feature_association.all.tsv.gz",
  },
  {
    label: "Chemical to disease or phenotypic feature association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/chemical_to_disease_or_phenotypic_feature_association.all.tsv.gz",
  },
  {
    label: "Chemical to pathway association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/chemical_to_pathway_association.all.tsv.gz",
  },
  {
    label: "Correlated gene to disease association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/correlated_gene_to_disease_association.all.tsv.gz",
  },
  {
    label: "Disease or phenotypic feature to genetic inheritance association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/disease_or_phenotypic_feature_to_genetic_inheritance_association.all.tsv.gz",
  },
  {
    label: "Disease or phenotypic feature to location association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/disease_or_phenotypic_feature_to_location_association.all.tsv.gz",
  },
  {
    label: "Disease to phenotypic feature association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/disease_to_phenotypic_feature_association.all.tsv.gz",
  },
  {
    label: "Gene to expression site association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/gene_to_expression_site_association.all.tsv.gz",
  },
  {
    label: "Gene to gene homology association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/gene_to_gene_homology_association.all.tsv.gz",
  },
  {
    label: "Gene to pathway association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/gene_to_pathway_association.all.tsv.gz",
  },
  {
    label: "Gene to phenotypic feature association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/gene_to_phenotypic_feature_association.all.tsv.gz",
  },
  {
    label: "Genotype to disease association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/genotype_to_disease_association.all.tsv.gz",
  },
  {
    label: "Macromolecular machine to biological process association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/macromolecular_machine_to_biological_process_association.all.tsv.gz",
  },
  {
    label: "Macromolecular machine to molecular activity association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/macromolecular_machine_to_molecular_activity_association.all.tsv.gz",
  },
  {
    label: "Pairwise gene to gene interaction",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/pairwise_gene_to_gene_interaction.all.tsv.gz",
  },
  {
    label: "Variant to disease association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/variant_to_disease_association.all.tsv.gz",
  },
  {
    label: "Variant to gene association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/variant_to_gene_association.all.tsv.gz",
  },
  {
    label: "Variant to phenotypic feature association",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/tsv/all_associations/variant_to_phenotypic_feature_association.all.tsv.gz",
  },
];

export const derivedArtifacts: DownloadItem[] = [
  {
    label: "Phenio SQLite (semsql)",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/phenio.db.gz",
  },
  {
    label: "Solr Data",
    url: "https://data.monarchinitiative.org/monarch-kg/latest/solr.tar.gz",
  },
];
