import { describe, expect, it, vi } from "vitest";
import {
  emptyFilters,
  useAssociationFilters,
  type SourceFilters,
} from "@/composables/use-source-dashboard";

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { infores: "monarchinitiative" } }),
}));

describe("emptyFilters", () => {
  it("returns an object with all empty string values", () => {
    const filters = emptyFilters();
    expect(Object.values(filters).every((v) => v === "")).toBe(true);
  });

  it("contains all expected keys", () => {
    const filters = emptyFilters();
    const expectedKeys: (keyof SourceFilters)[] = [
      "category",
      "subjectCategory",
      "objectCategory",
      "predicate",
      "subjectTaxonLabel",
      "objectTaxonLabel",
      "knowledgeLevel",
      "agentType",
      "providedBy",
      "negated",
      "primaryKnowledgeSource",
      "search",
    ];
    expect(Object.keys(filters).sort()).toEqual(expectedKeys.sort());
  });
});

describe("useAssociationFilters", () => {
  it("initializes with empty filters", () => {
    const { filters } = useAssociationFilters();
    expect(Object.values(filters).every((v) => v === "")).toBe(true);
  });

  it("initializes with default offset and limit", () => {
    const { offset, limit } = useAssociationFilters();
    expect(offset.value).toBe(0);
    expect(limit.value).toBe(20);
  });

  it("hasActiveFilters is false initially", () => {
    const { hasActiveFilters } = useAssociationFilters();
    expect(hasActiveFilters.value).toBe(false);
  });

  it("setFilter updates the filter value and resets offset", () => {
    const { filters, offset, setFilter } = useAssociationFilters();
    offset.value = 40;
    setFilter("predicate", "biolink:has_phenotype");
    expect(filters.predicate).toBe("biolink:has_phenotype");
    expect(offset.value).toBe(0);
  });

  it("setFilter makes hasActiveFilters true", () => {
    const { hasActiveFilters, setFilter } = useAssociationFilters();
    setFilter("category", "biolink:GeneToPhenotypicFeatureAssociation");
    expect(hasActiveFilters.value).toBe(true);
  });

  it("clearFilters resets all filters and offset", () => {
    const { filters, offset, clearFilters, setFilter, hasActiveFilters } =
      useAssociationFilters();

    setFilter("predicate", "biolink:has_phenotype");
    setFilter("subjectCategory", "biolink:Gene");
    offset.value = 60;

    clearFilters();

    expect(Object.values(filters).every((v) => v === "")).toBe(true);
    expect(offset.value).toBe(0);
    expect(hasActiveFilters.value).toBe(false);
  });

  it("filterQueries builds correct Solr fq entries", () => {
    const { filterQueries, setFilter } = useAssociationFilters();

    setFilter("category", "biolink:Association");
    setFilter("predicate", "biolink:has_phenotype");
    setFilter("negated", "true");

    expect(filterQueries.value).toContain('category:"biolink:Association"');
    expect(filterQueries.value).toContain('predicate:"biolink:has_phenotype"');
    expect(filterQueries.value).toContain("negated:true");
  });

  it("filterQueries excludes empty filter values", () => {
    const { filterQueries, setFilter } = useAssociationFilters();
    setFilter("predicate", "biolink:has_phenotype");
    expect(filterQueries.value).toHaveLength(1);
  });

  it("negated filter omits quotes around value", () => {
    const { filterQueries, setFilter } = useAssociationFilters();
    setFilter("negated", "true");
    expect(filterQueries.value).toContain("negated:true");
    expect(filterQueries.value).not.toContain('negated:"true"');
  });
});
