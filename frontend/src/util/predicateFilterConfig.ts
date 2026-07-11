/**
 * Predicate filtering config for association tables.
 *
 * Some sections combine edges with different predicates under one section key
 * (e.g. the drug-indications section mixes biolink:treats from MEDIC/FDA and
 * the weaker biolink:treats_or_applied_or_studied_to_treat from CTD). Those
 * sections default to the strong predicate (indications) and offer a checkbox
 * to expand the table to the weaker, investigational relationship.
 */

/**
 * section keys (ac.key) whose table offers the indications/investigational
 * toggle
 */
const PREDICATE_FILTERABLE = new Set<string>(["drug_indications"]);

/** whether a section supports the predicate expand toggle */
export const isPredicateFilterable = (sectionKey: string): boolean =>
  PREDICATE_FILTERABLE.has(sectionKey);

/**
 * the predicate a filterable section shows by default (toggle unchecked). When
 * the weaker predicate is also present, the table is scoped to just this one
 * until the user opts in.
 */
const DEFAULT_PREDICATE: Record<string, string> = {
  drug_indications: "biolink:treats",
};

/** the default predicate for a section, if it is filterable */
export const defaultPredicateFor = (sectionKey: string): string | undefined =>
  DEFAULT_PREDICATE[sectionKey];

/** checkbox label to expand a section beyond its default predicate */
const EXPAND_LABEL: Record<string, string> = {
  drug_indications: "Include investigational (studied/applied) treatments",
};

/** human-readable label for the expand toggle */
export const expandLabelFor = (sectionKey: string): string =>
  EXPAND_LABEL[sectionKey] ?? "Include additional relationships";

/** friendly labels for predicates shown in association tables */
const PREDICATE_LABELS: Record<string, string> = {
  "biolink:treats": "Indication",
  "biolink:treats_or_applied_or_studied_to_treat": "Investigational",
};

/** human-readable label for a predicate value */
export const formatPredicate = (predicate: string): string =>
  PREDICATE_LABELS[predicate] ??
  predicate
    .replace("biolink:", "")
    .replace(/_/g, " ")
    .replace(/^./, (c) => c.toUpperCase());
