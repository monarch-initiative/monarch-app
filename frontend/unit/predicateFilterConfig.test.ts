import { describe, expect, test } from "vitest";
import {
  defaultPredicatesFor,
  expandLabelFor,
  isPredicateFilterable,
  predicateFilterState,
} from "@/util/predicateFilterConfig";

const TREATS = "biolink:treats";
const PREVENTS = "biolink:preventative_for_condition";
const CTD = "biolink:treats_or_applied_or_studied_to_treat";

describe("isPredicateFilterable", () => {
  test("drug_indications is filterable", () => {
    expect(isPredicateFilterable("drug_indications")).toBe(true);
  });

  test("other sections are not", () => {
    expect(
      isPredicateFilterable("biolink:DiseaseToPhenotypicFeatureAssociation"),
    ).toBe(false);
    expect(
      isPredicateFilterable("clinical_measurement_correlated_phenotypes"),
    ).toBe(false);
  });
});

describe("defaultPredicatesFor", () => {
  test("drug_indications defaults to the approved uses", () => {
    expect(defaultPredicatesFor("drug_indications")).toEqual([
      TREATS,
      PREVENTS,
    ]);
  });

  test("undefined for non-filterable sections", () => {
    expect(
      defaultPredicatesFor("biolink:GeneToPhenotypicFeatureAssociation"),
    ).toBe(undefined);
  });
});

describe("expandLabelFor", () => {
  test("drug_indications expands to investigational uses", () => {
    expect(expandLabelFor("drug_indications")).toBe(
      "Include investigational uses (clinical trials, studied, applied)",
    );
  });

  test("falls back to a generic label", () => {
    expect(expandLabelFor("something_else")).toBe(
      "Include additional relationships",
    );
  });
});

describe("predicateFilterState", () => {
  test("no filter and no toggle before the facet loads (empty options)", () => {
    expect(predicateFilterState("drug_indications", [], false)).toEqual({
      showToggle: false,
      filterIds: [],
    });
  });

  test("both predicates present, unchecked → scope to the default, show toggle", () => {
    expect(
      predicateFilterState("drug_indications", [TREATS, CTD], false),
    ).toEqual({ showToggle: true, filterIds: [TREATS] });
  });

  test("both predicates present, checked → no filter, toggle still shown", () => {
    expect(
      predicateFilterState("drug_indications", [TREATS, CTD], true),
    ).toEqual({ showToggle: true, filterIds: [] });
  });

  test("both default predicates present → scope to both", () => {
    expect(
      predicateFilterState("drug_indications", [TREATS, PREVENTS, CTD], false),
    ).toEqual({ showToggle: true, filterIds: [TREATS, PREVENTS] });
  });

  test("only default predicates present → no toggle, no filter", () => {
    expect(
      predicateFilterState("drug_indications", [TREATS, PREVENTS], false),
    ).toEqual({ showToggle: false, filterIds: [] });
  });

  test("only the default predicate present → no toggle, no filter", () => {
    expect(predicateFilterState("drug_indications", [TREATS], false)).toEqual({
      showToggle: false,
      filterIds: [],
    });
  });

  test("only the weaker predicate present → no toggle, no filter (avoid empty table)", () => {
    expect(predicateFilterState("drug_indications", [CTD], false)).toEqual({
      showToggle: false,
      filterIds: [],
    });
  });

  test("non-filterable section → no toggle, no filter", () => {
    expect(
      predicateFilterState(
        "biolink:GeneToPhenotypicFeatureAssociation",
        [TREATS, CTD],
        false,
      ),
    ).toEqual({ showToggle: false, filterIds: [] });
  });
});
