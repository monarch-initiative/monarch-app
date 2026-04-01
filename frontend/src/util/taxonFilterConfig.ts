/**
 * Taxon filtering config for association tables.
 *
 * Each entry maps a category to the Solr field that holds the "interesting"
 * taxon — i.e. the side that is NOT the page entity. Faceting and filtering use
 * only this single field so counts are accurate and selecting a taxon actually
 * narrows the results.
 */

type TaxonField = "subject_taxon_label" | "object_taxon_label";

const TAXON_FILTER_FIELD: Record<string, TaxonField> = {
  /** Orthologs on gene pages — filter by the ortholog's species */
  "biolink:GeneToGeneHomologyAssociation": "object_taxon_label",
  /** Gene-phenotype on disease pages — filter by the gene's species */
  "biolink:GeneToPhenotypicFeatureAssociation": "subject_taxon_label",
  /** Genotype-disease — filter by the genotype's species */
  "biolink:GenotypeToDiseaseAssociation": "subject_taxon_label",
};

/** Get the taxon field for a category, or undefined if not filterable */
export const taxonFieldFor = (categoryId: string): TaxonField | undefined =>
  TAXON_FILTER_FIELD[categoryId] ??
  (categoryId.includes("Interaction") ? "object_taxon_label" : undefined);

/** Check if a category supports taxon filtering */
export const isTaxonFilterable = (categoryId: string): boolean =>
  taxonFieldFor(categoryId) !== undefined;
