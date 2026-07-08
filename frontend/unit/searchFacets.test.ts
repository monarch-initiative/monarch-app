import { expect, test } from "vitest";
import { buildFacetOption } from "@/util/searchFacets";

test("taxon facet values keep source casing and are italic", () => {
  const option = buildFacetOption("in_taxon_label", {
    label: "Homo sapiens",
    count: 190,
  });
  expect(option.label).toBe("Homo sapiens");
  expect(option.italic).toBe(true);
  expect(option.count).toBe(190);
});

test("taxon facet does not title-case strain suffixes", () => {
  const option = buildFacetOption("in_taxon_label", {
    label: "Saccharomyces cerevisiae S288C",
  });
  /** regression: startCase would have produced "... S 288 C" */
  expect(option.label).toBe("Saccharomyces cerevisiae S288C");
  expect(option.italic).toBe(true);
});

test("non-taxon, non-category facet values are title-cased and not italic", () => {
  const option = buildFacetOption("some_other_facet", {
    label: "in vitro",
  });
  expect(option.label).toBe("In Vitro");
  expect(option.italic).toBe(false);
});

test("category facet values are not italic and get an icon", () => {
  const option = buildFacetOption("category", {
    label: "biolink:Disease",
  });
  expect(option.italic).toBe(false);
  expect(option.icon).toBeTruthy();
});
