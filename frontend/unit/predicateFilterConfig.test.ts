import { describe, expect, test } from "vitest";
import {
  defaultPredicateFor,
  expandLabelFor,
  isPredicateFilterable,
  predicateFilterState,
} from "@/util/predicateFilterConfig";

const TREATS = "biolink:treats";
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

describe("defaultPredicateFor", () => {
  test("drug_indications defaults to biolink:treats (indications)", () => {
    expect(defaultPredicateFor("drug_indications")).toBe("biolink:treats");
  });

  test("undefined for non-filterable sections", () => {
    expect(
      defaultPredicateFor("biolink:GeneToPhenotypicFeatureAssociation"),
    ).toBe(undefined);
  });
});

describe("expandLabelFor", () => {
  test("drug_indications expands to investigational treatments", () => {
    expect(expandLabelFor("drug_indications")).toBe(
      "Include investigational (studied/applied) treatments",
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
