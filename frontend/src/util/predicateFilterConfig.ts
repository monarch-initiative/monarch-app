/**
 * Predicate filtering config for association tables.
 *
 * The drug-indications section holds approved uses (biolink:treats,
 * biolink:preventative_for_condition, from drug labels) alongside weaker,
 * investigational relationships (in_clinical_trials_for, studied_to_treat,
 * applied_to_treat, CTD's treats_or_applied_or_studied_to_treat). It defaults
 * to the approved uses and offers a checkbox to expand the table to the
 * investigational ones. Contraindications and diagnostic uses are separate
 * sections (association_type_mappings.yaml), not part of this toggle.
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
 * the predicates a filterable section shows by default (toggle unchecked). When
 * a weaker predicate is also present, the table is scoped to these until the
 * user opts in.
 */
const DEFAULT_PREDICATES: Record<string, string[]> = {
  drug_indications: ["biolink:treats", "biolink:preventative_for_condition"],
};

/** the default predicates for a section, if it is filterable */
export const defaultPredicatesFor = (
  sectionKey: string,
): string[] | undefined => DEFAULT_PREDICATES[sectionKey];

/** checkbox label to expand a section beyond its default predicate */
const EXPAND_LABEL: Record<string, string> = {
  drug_indications:
    "Include investigational uses (clinical trials, studied, applied)",
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
 * loads) so we can discover whether a weaker predicate is present. Once options
 * are known: show the toggle only when both a default and a weaker predicate
 * exist, and scope the table to the default predicates until the user opts in.
 * When only one kind is present, don't filter — this avoids an empty table for
 * nodes that carry only the weaker edges.
 */
export const predicateFilterState = (
  sectionKey: string,
  optionIds: string[],
  includeInvestigational: boolean,
): PredicateFilterState => {
  const noFilter: PredicateFilterState = { showToggle: false, filterIds: [] };
  const defaults = defaultPredicatesFor(sectionKey);
  if (!defaults || optionIds.length === 0) return noFilter;

  const presentDefaults = optionIds.filter((id) => defaults.includes(id));
  const hasOther = optionIds.some((id) => !defaults.includes(id));
  if (!presentDefaults.length || !hasOther) return noFilter;

  return {
    showToggle: true,
    filterIds: includeInvestigational ? [] : presentDefaults,
  };
};
