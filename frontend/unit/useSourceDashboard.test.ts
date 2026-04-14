import { nextTick } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { url } from "@/composables/use-param";
import {
  emptyFilters,
  useAssociationFilters,
  useSourceDashboard,
  type SourceFilters,
} from "@/composables/use-source-dashboard";

const mockRoute = { params: { infores: "monarchinitiative" } };
vi.mock("vue-router", () => ({
  useRoute: () => mockRoute,
}));

/** clear shared URL state between tests to prevent leakage */
beforeEach(() => {
  for (const key of Object.keys(url.value)) {
    delete url.value[key];
  }
});

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

describe("useSourceDashboard", () => {
  it("returns inforesId from route params", () => {
    mockRoute.params = { infores: "monarchinitiative" };
    const { inforesId } = useSourceDashboard();
    expect(inforesId.value).toBe("infores:monarchinitiative");
  });

  it("returns sourceName from RESOURCE_NAME_MAP for known key", () => {
    mockRoute.params = { infores: "hpo-annotations" };
    const { sourceName } = useSourceDashboard();
    expect(sourceName.value).toBe("Human Phenotype Ontology Annotations");
  });

  it("returns uppercased key for unknown source", () => {
    mockRoute.params = { infores: "unknown-source" };
    const { sourceName } = useSourceDashboard();
    expect(sourceName.value).toBe("UNKNOWN-SOURCE");
  });

  it("returns 'Unknown Source' when route param is empty", () => {
    mockRoute.params = { infores: "" };
    const { sourceName } = useSourceDashboard();
    expect(sourceName.value).toBe("Unknown Source");
  });

  it("returns all expected properties", () => {
    mockRoute.params = { infores: "monarchinitiative" };
    const result = useSourceDashboard();
    expect(result).toHaveProperty("inforesId");
    expect(result).toHaveProperty("sourceName");
    expect(result).toHaveProperty("filters");
    expect(result).toHaveProperty("filterQueries");
    expect(result).toHaveProperty("offset");
    expect(result).toHaveProperty("limit");
    expect(result).toHaveProperty("setFilter");
    expect(result).toHaveProperty("clearFilters");
    expect(result).toHaveProperty("hasActiveFilters");
  });

  it("setFilter and clearFilters work correctly", () => {
    mockRoute.params = { infores: "monarchinitiative" };
    const { filters, setFilter, clearFilters, hasActiveFilters } =
      useSourceDashboard();
    setFilter("predicate", "biolink:has_phenotype");
    expect(filters.predicate).toBe("biolink:has_phenotype");
    expect(hasActiveFilters.value).toBe(true);
    clearFilters();
    expect(filters.predicate).toBe("");
    expect(hasActiveFilters.value).toBe(false);
  });
});

describe("URL sync (deep linking)", () => {
  it("setFilter updates URL query params", async () => {
    const { setFilter } = useAssociationFilters();
    setFilter("category", "biolink:GeneToPhenotypicFeatureAssociation");
    await nextTick();
    expect(url.value.category).toBe(
      "biolink:GeneToPhenotypicFeatureAssociation",
    );
  });

  it("multiple filters are reflected in URL", async () => {
    const { setFilter } = useAssociationFilters();
    setFilter("predicate", "biolink:has_phenotype");
    setFilter("subjectTaxonLabel", "Homo sapiens");
    await nextTick();
    expect(url.value.predicate).toBe("biolink:has_phenotype");
    expect(url.value.subjectTaxonLabel).toBe("Homo sapiens");
  });

  it("clearFilters removes filter keys from URL", async () => {
    const { setFilter, clearFilters } = useAssociationFilters();
    setFilter("category", "biolink:Association");
    setFilter("predicate", "biolink:has_phenotype");
    await nextTick();
    clearFilters();
    await nextTick();
    expect(url.value.category).toBeUndefined();
    expect(url.value.predicate).toBeUndefined();
  });

  it("initializes filters from existing URL params", async () => {
    url.value.category = "biolink:Association";
    url.value.predicate = "biolink:has_phenotype";
    await nextTick();
    const { filters } = useAssociationFilters();
    expect(filters.category).toBe("biolink:Association");
    expect(filters.predicate).toBe("biolink:has_phenotype");
  });

  it("offset syncs to URL when non-zero", async () => {
    const { offset } = useAssociationFilters();
    offset.value = 40;
    await nextTick();
    expect(url.value.offset).toBe("40");
  });

  it("limit syncs to URL when changed from default", async () => {
    const { limit } = useAssociationFilters();
    limit.value = 50;
    await nextTick();
    expect(url.value.limit).toBe("50");
  });

  it("default offset and limit do not appear in URL", async () => {
    useAssociationFilters();
    await nextTick();
    expect(url.value.offset).toBeUndefined();
    expect(url.value.limit).toBeUndefined();
  });

  it("setFilter resets offset in URL back to page 1", async () => {
    const { offset, setFilter } = useAssociationFilters();
    offset.value = 60;
    await nextTick();
    expect(url.value.offset).toBe("60");
    setFilter("predicate", "biolink:has_phenotype");
    await nextTick();
    expect(offset.value).toBe(0);
    expect(url.value.offset).toBeUndefined();
  });
});
