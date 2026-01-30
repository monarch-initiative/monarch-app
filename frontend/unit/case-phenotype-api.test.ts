import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  CaseLimitExceededError,
  getCasePhenotypeMatrix,
} from "@/api/case-phenotype";

describe("getCasePhenotypeMatrix", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    // Reset fetch mock before each test
    vi.resetAllMocks();
  });

  afterEach(() => {
    // Restore original fetch after each test
    global.fetch = originalFetch;
  });

  it("should fetch matrix from backend", async () => {
    const mockResponse = {
      disease_id: "MONDO:0007078",
      disease_name: "Achondroplasia",
      total_cases: 85,
      total_phenotypes: 150,
      cases: [],
      phenotypes: [],
      bins: [],
      cells: {},
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await getCasePhenotypeMatrix("MONDO:0007078");
    expect(result).not.toBeNull();
    expect(result!.diseaseId).toBe("MONDO:0007078");
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/case-phenotype-matrix/MONDO"),
    );
  });

  it("should pass direct parameter", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          disease_id: "MONDO:0007078",
          total_cases: 0,
          total_phenotypes: 0,
          cases: [],
          phenotypes: [],
          bins: [],
          cells: {},
        }),
    });

    await getCasePhenotypeMatrix("MONDO:0007078", { direct: false });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("direct=false"),
    );
  });

  it("should pass limit parameter", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          disease_id: "MONDO:0007078",
          total_cases: 0,
          total_phenotypes: 0,
          cases: [],
          phenotypes: [],
          bins: [],
          cells: {},
        }),
    });

    await getCasePhenotypeMatrix("MONDO:0007078", { limit: 500 });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("limit=500"),
    );
  });

  it("should throw CaseLimitExceededError on over-limit error", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: () =>
        Promise.resolve({ detail: "Case count (500) exceeds limit (200)" }),
    });

    await expect(getCasePhenotypeMatrix("MONDO:0005071")).rejects.toThrow(
      CaseLimitExceededError,
    );
  });

  it("should throw generic error on other API errors", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: "Disease not found" }),
    });

    await expect(getCasePhenotypeMatrix("MONDO:9999999")).rejects.toThrow(
      "API error (404): Disease not found",
    );
  });

  it("should use default values for options", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          disease_id: "MONDO:0007078",
          total_cases: 0,
          total_phenotypes: 0,
          cases: [],
          phenotypes: [],
          bins: [],
          cells: {},
        }),
    });

    await getCasePhenotypeMatrix("MONDO:0007078");

    const call = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0];
    expect(call).toContain("direct=true");
    expect(call).toContain("limit=200");
  });
});
