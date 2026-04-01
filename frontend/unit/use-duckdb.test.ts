import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useDuckDB } from "@/composables/use-duckdb";

// Mock DuckDB WASM module
vi.mock("@duckdb/duckdb-wasm", () => ({
  selectBundle: vi.fn().mockResolvedValue({
    mainModule: "mock-module",
    mainWorker: "mock-worker",
  }),
  AsyncDuckDB: vi.fn().mockImplementation(() => ({
    instantiate: vi.fn().mockResolvedValue(undefined),
    connect: vi.fn().mockResolvedValue({
      query: vi.fn().mockResolvedValue({
        toArray: vi
          .fn()
          .mockReturnValue([
            { toJSON: () => ({ id: 1, name: "test" }) },
            { toJSON: () => ({ id: 2, name: "test2" }) },
          ]),
        schema: {
          fields: [{ name: "id" }, { name: "name" }],
        },
      }),
      close: vi.fn().mockResolvedValue(undefined),
    }),
    terminate: vi.fn().mockResolvedValue(undefined),
  })),
  ConsoleLogger: vi.fn().mockImplementation(() => ({})),
  LogLevel: {
    DEBUG: 0,
    INFO: 1,
    WARNING: 2,
    ERROR: 3,
  },
}));

// Mock Worker
global.Worker = vi.fn().mockImplementation(() => ({
  postMessage: vi.fn(),
  terminate: vi.fn(),
}));

describe("useDuckDB", () => {
  let duckDB: ReturnType<typeof useDuckDB>;

  beforeEach(() => {
    duckDB = useDuckDB();
    vi.clearAllMocks();
  });

  afterEach(async () => {
    if (duckDB.isInitialized.value) {
      await duckDB.cleanup();
    }
  });

  describe("initialization", () => {
    it("should initialize DuckDB instance successfully", async () => {
      expect(duckDB.isInitialized.value).toBe(false);
      expect(duckDB.db.value).toBe(null);
      expect(duckDB.connection.value).toBe(null);

      await duckDB.initDB();

      expect(duckDB.isInitialized.value).toBe(true);
      expect(duckDB.db.value).toBeDefined();
      expect(duckDB.connection.value).toBeDefined();
      expect(duckDB.error.value).toBe(null);
    });

    it("should not reinitialize if already initialized", async () => {
      await duckDB.initDB();
      const firstDB = duckDB.db.value;

      await duckDB.initDB();
      expect(duckDB.db.value).toBe(firstDB);
    });

    it("should handle initialization errors", async () => {
      // Create a new instance to test error handling
      const errorDB = useDuckDB();
      const mockError = new Error("Init failed");

      // Mock the AsyncDuckDB constructor to throw an error
      const { AsyncDuckDB } = await import("@duckdb/duckdb-wasm");
      vi.mocked(AsyncDuckDB).mockImplementationOnce(() => {
        throw mockError;
      }) as any;

      await expect(errorDB.initDB()).rejects.toThrow("Init failed");
      expect(errorDB.error.value).toBe("Init failed");
      expect(errorDB.isInitialized.value).toBe(false);
    });

    it("should set loading state during initialization", async () => {
      expect(duckDB.isLoading.value).toBe(false);

      const initPromise = duckDB.initDB();
      expect(duckDB.isLoading.value).toBe(true);

      await initPromise;
      expect(duckDB.isLoading.value).toBe(false);
    });
  });

  describe("parquet loading", () => {
    beforeEach(async () => {
      await duckDB.initDB();
    });

    it("should load parquet file successfully", async () => {
      const url = "https://example.com/test.parquet";
      const tableName = "test_table";

      await expect(duckDB.loadParquet(url, tableName)).resolves.not.toThrow();
      expect(duckDB.error.value).toBe(null);
    });

    it("should fail if not initialized", async () => {
      const uninitializedDB = useDuckDB();
      await expect(
        uninitializedDB.loadParquet("test.parquet", "test"),
      ).rejects.toThrow("DuckDB not initialized");
    });

    it("should handle parquet loading errors", async () => {
      const mockError = new Error("Parquet load failed");
      vi.mocked(duckDB.connection.value!.query).mockRejectedValueOnce(
        mockError,
      );

      await expect(
        duckDB.loadParquet("invalid.parquet", "test"),
      ).rejects.toThrow("Parquet load failed");
      expect(duckDB.error.value).toBe("Parquet load failed");
    });
  });

  describe("query execution", () => {
    beforeEach(async () => {
      await duckDB.initDB();
    });

    it("should execute SQL query successfully", async () => {
      const result = await duckDB.query("SELECT 1 as test");

      expect(result).toEqual({
        data: [
          { id: 1, name: "test" },
          { id: 2, name: "test2" },
        ],
        columns: ["id", "name"],
        rowCount: 2,
      });
      expect(duckDB.error.value).toBe(null);
    });

    it("should fail if not initialized", async () => {
      const uninitializedDB = useDuckDB();
      await expect(uninitializedDB.query("SELECT 1")).rejects.toThrow(
        "DuckDB not initialized",
      );
    });

    it("should handle query errors", async () => {
      const mockError = new Error("Invalid SQL");
      vi.mocked(duckDB.connection.value!.query).mockRejectedValueOnce(
        mockError,
      );

      await expect(duckDB.query("INVALID SQL")).rejects.toThrow("Invalid SQL");
      expect(duckDB.error.value).toBe("Invalid SQL");
    });

    it("should set loading state during query execution", async () => {
      expect(duckDB.isLoading.value).toBe(false);

      const queryPromise = duckDB.query("SELECT 1");
      expect(duckDB.isLoading.value).toBe(true);

      await queryPromise;
      expect(duckDB.isLoading.value).toBe(false);
    });
  });

  describe("cleanup", () => {
    it("should clean up resources properly", async () => {
      await duckDB.initDB();
      expect(duckDB.isInitialized.value).toBe(true);

      await duckDB.cleanup();

      expect(duckDB.connection.value).toBe(null);
      expect(duckDB.db.value).toBe(null);
      expect(duckDB.isInitialized.value).toBe(false);
    });

    it("should handle cleanup when not initialized", async () => {
      await expect(duckDB.cleanup()).resolves.not.toThrow();
    });
  });

  describe("configuration", () => {
    it("should use custom URLs when provided", async () => {
      const customConfig = {
        wasmUrl: "https://custom.com/duckdb.wasm",
        workerUrl: "https://custom.com/worker.js",
      };

      const customDB = useDuckDB(customConfig);
      await customDB.initDB();

      expect(customDB.isInitialized.value).toBe(true);
    });
  });
});
