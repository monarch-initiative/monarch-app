// Maps category IDs  and some known labels to display titles.
const TITLES_BY_ID: Record<string, string> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": "Disease Phenotypes",
  "biolink:CausalGeneToDiseaseAssociation": "Causal Genes",
  "biolink:GeneToPhenotypicFeatureAssociation": "Causal Gene Phenotypes",
  correlated_gene_to_disease: "Correlated Genes",
  "biolink:GenotypeAsAModelOfDiseaseAssociation": "Disease Models",
  "biolink:VariantToDiseaseAssociation": "Disease Variants",
};

export function sectionTitle(
  categoryId: string,
  fallbackLabel?: string,
): string {
  return TITLES_BY_ID[categoryId] ?? fallbackLabel ?? categoryId;
}
