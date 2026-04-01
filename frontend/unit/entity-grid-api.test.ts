/** Tests for entity-grid API client */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getEntityGrid } from "@/api/entity-grid";

describe("getEntityGrid", () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetch);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    mockFetch.mockReset();
  });

  it("should send multiple row_association_category params", async () => {
    // Mock successful response
    mockFetch.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          context_id: "MONDO:0005148",
          context_name: "Test Disease",
          context_category: "biolink:Disease",
          total_columns: 0,
          total_rows: 0,
          columns: [],
          rows: [],
          bins: [],
          cells: {},
        }),
        { status: 200 },
      ),
    );

    await getEntityGrid("MONDO:0005148", {
      columnAssociationCategory: ["biolink:CaseToDiseaseAssociation"],
      rowAssociationCategory: [
        "biolink:DiseaseToPhenotypicFeatureAssociation",
        "biolink:CaseToPhenotypicFeatureAssociation",
      ],
    });

    // Verify fetch was called
    expect(mockFetch).toHaveBeenCalledTimes(1);

    // Get the URL that was called
    const calledUrl = mockFetch.mock.calls[0][0] as string;
    const url = new URL(calledUrl);
    const params = url.searchParams;

    // Should have multiple row_association_category params
    const rowCategories = params.getAll("row_association_category");
    expect(rowCategories).toHaveLength(2);
    expect(rowCategories).toContain(
      "biolink:DiseaseToPhenotypicFeatureAssociation",
    );
    expect(rowCategories).toContain(
      "biolink:CaseToPhenotypicFeatureAssociation",
    );
  });

  it("should work with single row_association_category", async () => {
    mockFetch.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          context_id: "MONDO:0005148",
          context_name: "Test Disease",
          context_category: "biolink:Disease",
          total_columns: 0,
          total_rows: 0,
          columns: [],
          rows: [],
          bins: [],
          cells: {},
        }),
        { status: 200 },
      ),
    );

    await getEntityGrid("MONDO:0005148", {
      columnAssociationCategory: ["biolink:CaseToDiseaseAssociation"],
      rowAssociationCategory: ["biolink:DiseaseToPhenotypicFeatureAssociation"],
    });

    const calledUrl = mockFetch.mock.calls[0][0] as string;
    const url = new URL(calledUrl);
    const params = url.searchParams;

    const rowCategories = params.getAll("row_association_category");
    expect(rowCategories).toHaveLength(1);
    expect(rowCategories).toContain(
      "biolink:DiseaseToPhenotypicFeatureAssociation",
    );
  });
});
