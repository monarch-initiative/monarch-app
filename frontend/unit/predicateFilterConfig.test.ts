import { describe, expect, test } from "vitest";
import {
  defaultPredicateFor,
  expandLabelFor,
  formatPredicate,
  isPredicateFilterable,
} from "@/util/predicateFilterConfig";

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

describe("formatPredicate", () => {
  test("uses friendly labels for the treatment predicates", () => {
    expect(formatPredicate("biolink:treats")).toBe("Indication");
    expect(
      formatPredicate("biolink:treats_or_applied_or_studied_to_treat"),
    ).toBe("Investigational");
  });

  test("falls back to a de-prefixed, spaced label", () => {
    expect(formatPredicate("biolink:correlated_with")).toBe("Correlated with");
  });
});
