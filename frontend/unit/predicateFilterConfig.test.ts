import { describe, expect, test } from "vitest";
import {
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

describe("formatPredicate", () => {
  test("uses friendly labels for the treatment predicates", () => {
    expect(formatPredicate("biolink:treats")).toBe("Treats");
    expect(
      formatPredicate("biolink:treats_or_applied_or_studied_to_treat"),
    ).toBe("Applied or studied to treat");
  });

  test("falls back to a de-prefixed, spaced label", () => {
    expect(formatPredicate("biolink:correlated_with")).toBe("Correlated with");
  });
});
