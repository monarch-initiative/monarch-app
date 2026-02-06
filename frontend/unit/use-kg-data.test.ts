import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useKGData } from "@/composables/use-kg-data";

// Create mock functions that can be accessed in tests
const mockInitDB = vi.fn().mockResolvedValue(undefined);
const mockLoadParquet = vi.fn().mockResolvedValue(undefined);
const mockQuery = vi.fn().mockResolvedValue({
  data: [{ count: 100 }],
  columns: ["count"],
  rowCount: 1,
});
const mockCleanup = vi.fn().mockResolvedValue(undefined);

// Mock the dependencies
vi.mock("@/composables/use-duckdb", () => ({
  useDuckDB: vi.fn(() => ({
    initDB: mockInitDB,
    loadParquet: mockLoadParquet,
    query: mockQuery,
    cleanup: mockCleanup,
    isInitialized: { value: false },
    isLoading: { value: false },
    error: { value: null },
  })),
}));

vi.mock("@/api/kg-version", () => ({
  getLatestKGReleaseDate: vi.fn().mockResolvedValue("2025-07-09"),
  getKGSourceUrl: vi
    .fn()
    .mockResolvedValue(
      "https://data.monarchinitiative.org/monarch-kg/2025-07-09",
    ),
}));

describe("useKGData", () => {
  let kgData: ReturnType<typeof useKGData>;

  beforeEach(() => {
    kgData = useKGData();
    vi.clearAllMocks();
    // Reset mocks to their default behavior
    mockInitDB.mockResolvedValue(undefined);
    mockLoadParquet.mockResolvedValue(undefined);
    mockQuery.mockResolvedValue({
      data: [{ count: 100 }],
      columns: ["count"],
      rowCount: 1,
    });
    mockCleanup.mockResolvedValue(undefined);
  });

  afterEach(async () => {
    await kgData.cleanup();
  });

  describe("initialization", () => {
    it("should initialize successfully", async () => {
      expect(kgData.kgVersion.value).toBe("");
      expect(kgData.kgSourceUrl.value).toBe("");

      await kgData.init();

      expect(kgData.kgVersion.value).toBe("2025-07-09");
      expect(kgData.kgSourceUrl.value).toBe(
        "https://data.monarchinitiative.org/monarch-kg/2025-07-09",
      );
      expect(kgData.error.value).toBe(null);
    });

    it("should handle initialization errors", async () => {
      mockInitDB.mockRejectedValueOnce(new Error("Init failed"));

      await expect(kgData.init()).rejects.toThrow("Init failed");
      expect(kgData.error.value).toBe("Init failed");
    });

    it("should fallback to default version on API failure", async () => {
      const { getLatestKGReleaseDate, getKGSourceUrl } =
        await import("@/api/kg-version");
      vi.mocked(getLatestKGReleaseDate).mockRejectedValueOnce(
        new Error("API failed"),
      );
      vi.mocked(getKGSourceUrl).mockRejectedValueOnce(new Error("API failed"));

      await kgData.init();

      expect(kgData.kgVersion.value).toBe("latest");
      expect(kgData.kgSourceUrl.value).toBe(
        "https://data.monarchinitiative.org/monarch-kg-dev/latest",
      );
    });

    it("should set loading state during initialization", async () => {
      expect(kgData.isLoading.value).toBe(false);

      const initPromise = kgData.init();
      expect(kgData.isLoading.value).toBe(true);

      await initPromise;
      expect(kgData.isLoading.value).toBe(false);
    });
  });

  describe("data source management", () => {
    beforeEach(async () => {
      await kgData.init();
    });

    it("should register data source correctly", () => {
      const config = {
        name: "nodes",
        url: "qc/node_report.parquet",
        description: "Node statistics",
      };

      kgData.registerDataSource(config);

      const source = kgData.getDataSource("nodes");
      expect(source).toBeDefined();
      expect(source?.name).toBe("nodes");
      expect(source?.url).toBe("qc/node_report.parquet");
      expect(source?.description).toBe("Node statistics");
      expect(source?.isLoaded).toBe(false);
      expect(source?.baseUrl).toBe(
        "https://data.monarchinitiative.org/monarch-kg/2025-07-09",
      );
    });

    it("should register data source with custom base URL", () => {
      const config = {
        name: "custom",
        url: "custom.parquet",
        baseUrl: "https://custom.com",
      };

      kgData.registerDataSource(config);

      const source = kgData.getDataSource("custom");
      expect(source?.baseUrl).toBe("https://custom.com");
    });

    it("should return undefined for non-existent data source", () => {
      const source = kgData.getDataSource("nonexistent");
      expect(source).toBeUndefined();
    });

    it("should track all registered data sources", () => {
      kgData.registerDataSource({ name: "source1", url: "file1.parquet" });
      kgData.registerDataSource({ name: "source2", url: "file2.parquet" });

      const allSources = kgData.getAllDataSources.value;
      expect(allSources).toHaveLength(2);
      expect(allSources.map((s) => s.name)).toContain("source1");
      expect(allSources.map((s) => s.name)).toContain("source2");
    });

    it("should clear all data sources", () => {
      kgData.registerDataSource({ name: "source1", url: "file1.parquet" });
      kgData.registerDataSource({ name: "source2", url: "file2.parquet" });

      expect(kgData.getAllDataSources.value).toHaveLength(2);

      kgData.clearDataSources();

      expect(kgData.getAllDataSources.value).toHaveLength(0);
    });
  });

  describe("data source loading", () => {
    beforeEach(async () => {
      await kgData.init();
    });

    it("should load data source successfully", async () => {
      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });

      expect(kgData.isDataSourceLoaded("nodes")).toBe(false);

      await kgData.loadDataSource("nodes");

      expect(kgData.isDataSourceLoaded("nodes")).toBe(true);
      const source = kgData.getDataSource("nodes");
      expect(source?.lastLoaded).toBeDefined();
      expect(source?.loadError).toBeUndefined();
    });

    it("should not reload already loaded data source", async () => {
      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });

      await kgData.loadDataSource("nodes");
      expect(mockLoadParquet).toHaveBeenCalledTimes(1);

      await kgData.loadDataSource("nodes");
      expect(mockLoadParquet).toHaveBeenCalledTimes(1); // Should not be called again
    });

    it("should handle loading errors", async () => {
      mockLoadParquet.mockRejectedValueOnce(new Error("Load failed"));

      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });

      await expect(kgData.loadDataSource("nodes")).rejects.toThrow(
        "Load failed",
      );

      const source = kgData.getDataSource("nodes");
      expect(source?.isLoaded).toBe(false);
      expect(source?.loadError).toBe("Load failed");
    });

    it("should fail to load non-existent data source", async () => {
      await expect(kgData.loadDataSource("nonexistent")).rejects.toThrow(
        "Data source 'nonexistent' not found",
      );
    });

    it("should construct correct URLs", async () => {
      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });
      await kgData.loadDataSource("nodes");

      expect(mockLoadParquet).toHaveBeenCalledWith(
        "https://data.monarchinitiative.org/monarch-kg/2025-07-09/qc/node_report.parquet",
        "nodes",
      );
    });
  });

  describe("query execution", () => {
    beforeEach(async () => {
      await kgData.init();
    });

    it("should execute query successfully", async () => {
      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });

      const result = await kgData.executeQuery(
        "SELECT COUNT(*) as count FROM nodes",
        ["nodes"],
      );

      expect(result).toEqual([{ count: 100 }]);
      expect(kgData.isDataSourceLoaded("nodes")).toBe(true);
    });

    it("should execute query without required sources", async () => {
      const result = await kgData.executeQuery("SELECT 1 as test");

      expect(result).toEqual([{ count: 100 }]);
    });

    it("should handle query errors", async () => {
      mockQuery.mockRejectedValueOnce(new Error("Invalid SQL"));

      await expect(kgData.executeQuery("INVALID SQL")).rejects.toThrow(
        "Invalid SQL",
      );
      expect(kgData.error.value).toBe("Invalid SQL");
    });

    it("should load required sources before query", async () => {
      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });
      kgData.registerDataSource({
        name: "edges",
        url: "qc/edge_report.parquet",
      });

      await kgData.executeQuery("SELECT * FROM nodes JOIN edges", [
        "nodes",
        "edges",
      ]);

      expect(kgData.isDataSourceLoaded("nodes")).toBe(true);
      expect(kgData.isDataSourceLoaded("edges")).toBe(true);
    });
  });

  describe("computed properties", () => {
    beforeEach(async () => {
      await kgData.init();
    });

    it("should track loaded data sources", async () => {
      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });
      kgData.registerDataSource({
        name: "edges",
        url: "qc/edge_report.parquet",
      });

      expect(kgData.getLoadedDataSources.value).toHaveLength(0);

      await kgData.loadDataSource("nodes");

      expect(kgData.getLoadedDataSources.value).toHaveLength(1);
      expect(kgData.getLoadedDataSources.value[0]?.name).toBe("nodes");
    });
  });

  describe("cleanup", () => {
    it("should cleanup resources properly", async () => {
      await kgData.init();
      kgData.registerDataSource({
        name: "nodes",
        url: "qc/node_report.parquet",
      });

      expect(kgData.getAllDataSources.value).toHaveLength(1);

      await kgData.cleanup();

      expect(kgData.getAllDataSources.value).toHaveLength(0);
      expect(mockCleanup).toHaveBeenCalled();
    });
  });
});
