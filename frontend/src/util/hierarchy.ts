/**
 * Categories that get a hierarchy widget, and the noun each one uses in its
 * title.
 *
 * Shared by SectionHierarchy (which reads the label) and TheTableOfContents
 * (which uses membership as one half of its render gate). Keeping one map
 * rather than a list plus a label lookup means a new category cannot end up in
 * only one of them — which would render an untitled widget, or no widget at
 * all, depending on which was updated.
 */
export const HIERARCHY_LABELS = new Map<string, string>([
  ["biolink:Disease", "Disease"],
  ["biolink:PhenotypicFeature", "Phenotype"],
  ["biolink:AnatomicalEntity", "Anatomical entity"],
  ["biolink:ClinicalMeasurement", "Clinical measurement"],
]);
