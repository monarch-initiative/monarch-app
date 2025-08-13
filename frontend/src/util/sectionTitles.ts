// Maps category IDs  and some known labels to display titles.
const TITLES_BY_ID: Record<string, string> = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": "Disease Phenotypes",
  "biolink:CausalGeneToDiseaseAssociation": "Causal Genes",
  "biolink:GeneToPhenotypicFeatureAssociation": "Causal Gene Phenotypes",
  "biolink:CorrelatedGeneToDiseaseAssociation": "Correlated Genes",
  "biolink:GenotypeToDiseaseAssociation": "Disease Models",
};

export function sectionTitle(
  categoryId: string,
  fallbackLabel?: string,
): string {
  return TITLES_BY_ID[categoryId] ?? fallbackLabel ?? categoryId;
}
