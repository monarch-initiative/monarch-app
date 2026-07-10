/**
 * Predicate filtering config for association tables.
 *
 * Some sections combine edges with different predicates under one section key
 * (e.g. the drug-indications section mixes biolink:treats from MEDIC and
 * biolink:treats_or_applied_or_studied_to_treat from CTD). Those sections offer
 * a "Filter by relationship" dropdown that scopes the table by predicate.
 */

/** section keys (ac.key) whose table should offer a predicate filter */
const PREDICATE_FILTERABLE = new Set<string>(["drug_indications"]);

/** whether a section supports predicate filtering */
export const isPredicateFilterable = (sectionKey: string): boolean =>
  PREDICATE_FILTERABLE.has(sectionKey);

/** friendly labels for predicates shown in the filter dropdown */
const PREDICATE_LABELS: Record<string, string> = {
  "biolink:treats": "Treats",
  "biolink:treats_or_applied_or_studied_to_treat":
    "Applied or studied to treat",
};

/** human-readable label for a predicate value */
export const formatPredicate = (predicate: string): string =>
  PREDICATE_LABELS[predicate] ??
  predicate
    .replace("biolink:", "")
    .replace(/_/g, " ")
    .replace(/^./, (c) => c.toUpperCase());
