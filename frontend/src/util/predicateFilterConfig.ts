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

export type PredicateFilterState = {
  /**
   * whether to show the expand toggle (both default and a weaker predicate
   * exist)
   */
  showToggle: boolean;
  /** predicates to scope the table to; [] means no filter */
  filterIds: string[];
};

/**
 * Derive a section's predicate-filter state from its available predicate
 * options and the current toggle state.
 *
 * The first fetch is intentionally unfiltered (optionIds empty until the facet
 * loads) so we can discover whether the weaker predicate is present. Once
 * options are known: show the toggle only when both the default and a weaker
 * predicate exist, and scope the table to the default predicate until the user
 * opts in. When only one predicate is present (or the default is absent), don't
 * filter — this avoids an empty table for nodes that carry only the weaker
 * edge.
 */
export const predicateFilterState = (
  sectionKey: string,
  optionIds: string[],
  includeInvestigational: boolean,
): PredicateFilterState => {
  const noFilter: PredicateFilterState = { showToggle: false, filterIds: [] };
  const defaultPredicate = defaultPredicateFor(sectionKey);
  if (!defaultPredicate || optionIds.length === 0) return noFilter;

  const hasDefault = optionIds.includes(defaultPredicate);
  const hasOther = optionIds.some((id) => id !== defaultPredicate);
  if (!hasDefault || !hasOther) return noFilter;

  return {
    showToggle: true,
    filterIds: includeInvestigational ? [] : [defaultPredicate],
  };
};
