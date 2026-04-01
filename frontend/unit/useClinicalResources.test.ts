import { describe, expect, it } from "vitest";
import type { Node } from "@/api/model";
import { useClinicalResources } from "@/composables/use-clinical-resources";

const asNode = (n: Partial<Node>) => n as Node;

describe("useClinicalResources", () => {
  it("returns empty arrays when node has no external_links or mappings", () => {
    const node = asNode({});
    const { clinicalResources, otherMappings, externalRefs } =
      useClinicalResources(node);

    expect(clinicalResources.value).toEqual([]);
    expect(otherMappings.value).toEqual([]);
    expect(externalRefs.value).toEqual([]);
  });

  it("builds entries from external_links with correct label, source, and tooltip", () => {
    const node = asNode({
      external_links: [
        { id: "OMIM:123", url: "https://omim.org/entry/123" },
        {
          id: "GARD:ABC",
          url: "https://rarediseases.info.nih.gov/diseases/abc",
        },
      ],
    });

    const { clinicalResources } = useClinicalResources(node);
    // Order follows RESOURCE_DEFS: OMIM ... GARD ...
    expect(clinicalResources.value.map((r) => r.id)).toEqual([
      "OMIM:123",
      "GARD:ABC",
    ]);

    const omim = clinicalResources.value[0];
    expect(omim.label).toBe("OMIM");
    expect(omim.source).toBe("external");
    expect(omim.url).toBe("https://omim.org/entry/123");
    expect(typeof omim.tooltip).toBe("string");
    expect(omim.tooltip!.toLowerCase()).toContain("mendelian");

    const gard = clinicalResources.value[1];
    expect(gard.label).toBe("GARD");
    expect(gard.source).toBe("external");
  });

  it("falls back to empty string for missing URLs", () => {
    const node = asNode({
      external_links: [{ id: "OMIM:999" }], // no url
    });
    const { clinicalResources } = useClinicalResources(node);
    expect(clinicalResources.value[0].url).toBe("");
  });

  it("uses mappings when external_links for a prefix are absent", () => {
    const node = asNode({
      mappings: [
        { id: "NORD:55", url: "https://rarediseases.org/55" },
        { id: "Orphanet:777", url: "https://www.orpha.net/777" },
      ],
    });
    const { clinicalResources } = useClinicalResources(node);
    // Order per RESOURCE_DEFS: OMIM, NORD, GARD, Orphanet, MEDGEN
    expect(clinicalResources.value.map((r) => r.id)).toEqual([
      "NORD:55",
      "Orphanet:777",
    ]);
    expect(clinicalResources.value[0].source).toBe("mapping");
    expect(clinicalResources.value[1].source).toBe("mapping");
  });

  it("prefers external over mapping when both exist for the same prefix", () => {
    const node = asNode({
      external_links: [{ id: "OMIM:1", url: "ext" }],
      mappings: [{ id: "OMIM:1", url: "map" }],
    });
    const { clinicalResources } = useClinicalResources(node);
    // Only one entry for OMIM:1, from external
    expect(clinicalResources.value).toHaveLength(1);
    expect(clinicalResources.value[0]).toMatchObject({
      id: "OMIM:1",
      url: "ext",
      source: "external",
      label: "OMIM",
    });
  });

  it("orders results by RESOURCE_DEFS, not by input order", () => {
    const node = asNode({
      external_links: [{ id: "MEDGEN:Z" }],
      mappings: [{ id: "NORD:X" }, { id: "GARD:Y" }],
    });
    const { clinicalResources } = useClinicalResources(node);
    // RESOURCE_DEFS order: OMIM, NORD, GARD, Orphanet, MEDGEN
    expect(clinicalResources.value.map((r) => r.id)).toEqual([
      "NORD:X",
      "GARD:Y",
      "MEDGEN:Z",
    ]);
  });

  it("otherMappings excludes clinical prefixes; externalRefs excludes clinical prefixes", () => {
    const node = asNode({
      mappings: [
        { id: "NORD:1", url: "m1" },
        { id: "XDB:2", url: "m2" }, // non-clinical
      ],
      external_links: [
        { id: "GARD:3", url: "e3" },
        { id: "YDB:4", url: "e4" }, // non-clinical
      ],
    });
    const { otherMappings, externalRefs } = useClinicalResources(node);
    expect(otherMappings.value.map((m) => m.id)).toEqual(["XDB:2"]);
    expect(externalRefs.value.map((l) => l.id)).toEqual(["YDB:4"]);
  });

  it("handles duplicates across different clinical prefixes independently", () => {
    const node = asNode({
      external_links: [{ id: "OMIM:9" }],
      mappings: [{ id: "GARD:9" }], // different prefix, both should appear
    });
    const { clinicalResources } = useClinicalResources(node);
    expect(clinicalResources.value.map((r) => r.id)).toEqual([
      "OMIM:9",
      "GARD:9",
    ]);
    expect(clinicalResources.value[0].source).toBe("external");
    expect(clinicalResources.value[1].source).toBe("mapping");
  });
});
