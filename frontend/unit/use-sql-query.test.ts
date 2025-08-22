import { beforeEach, describe, expect, it, vi } from "vitest";
import { useSqlQuery } from "@/composables/use-sql-query";

// Mock the useKGData composable
const mockExecuteQuery = vi.fn();
vi.mock("@/composables/use-kg-data", () => ({
  useKGData: vi.fn(() => ({
    executeQuery: mockExecuteQuery,
  })),
}));

describe("useSqlQuery", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockExecuteQuery.mockResolvedValue([
      { count: 100, category: "test" },
      { count: 200, category: "test2" },
    ]);
  });

  describe("SQL validation", () => {
    it("should validate safe SELECT queries", () => {
      const sqlQuery = useSqlQuery({
        sql: "SELECT * FROM nodes",
        dataSources: ["nodes"],
      });

      const result = sqlQuery.validateSQL("SELECT * FROM nodes WHERE id = 1");
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it("should reject dangerous queries", () => {
      const sqlQuery = useSqlQuery({
        sql: "SELECT * FROM nodes",
        dataSources: ["nodes"],
      });

      const result = sqlQuery.validateSQL("DROP TABLE nodes");
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(
        "Query contains potentially dangerous keyword: DROP",
      );
    });

    it("should reject non-SELECT queries", () => {
      const sqlQuery = useSqlQuery({
        sql: "SELECT * FROM nodes",
        dataSources: ["nodes"],
      });

      const result = sqlQuery.validateSQL("UPDATE nodes SET count = 0");
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain("Query must start with SELECT or WITH");
    });
  });

  describe("query execution", () => {
    it("should execute query successfully", async () => {
      const sqlQuery = useSqlQuery({
        sql: "SELECT COUNT(*) as count FROM nodes",
        dataSources: ["nodes"],
      });

      const result = await sqlQuery.executeQuery();

      expect(mockExecuteQuery).toHaveBeenCalledWith(
        "SELECT COUNT(*) as count FROM nodes",
        ["nodes"],
      );
      expect(result.data).toEqual([
        { count: 100, category: "test" },
        { count: 200, category: "test2" },
      ]);
      expect(result.columns).toEqual(["count", "category"]);
      expect(result.rowCount).toBe(2);
      expect(result.isFromCache).toBe(false);
    });

    it("should cache query results", async () => {
      const sqlQuery = useSqlQuery({
        sql: "SELECT COUNT(*) as count FROM nodes",
        dataSources: ["nodes"],
      });

      // First execution
      const result1 = await sqlQuery.executeQuery();
      expect(mockExecuteQuery).toHaveBeenCalledTimes(1);
      expect(result1.isFromCache).toBe(false);

      // Second execution should use cache
      const result2 = await sqlQuery.executeQuery();
      expect(mockExecuteQuery).toHaveBeenCalledTimes(1); // Still only called once
      expect(result2.isFromCache).toBe(true);
    });

    it("should handle query errors", async () => {
      mockExecuteQuery.mockRejectedValueOnce(new Error("Database error"));

      const sqlQuery = useSqlQuery({
        sql: "SELECT * FROM invalid_table",
        dataSources: ["nodes"],
      });

      await expect(sqlQuery.executeQuery()).rejects.toThrow("Database error");
      expect(sqlQuery.error.value).toBe("Database error");
    });
  });

  describe("single value extraction", () => {
    it("should extract single value from result", async () => {
      mockExecuteQuery.mockResolvedValueOnce([{ total: 500 }]);

      const sqlQuery = useSqlQuery({
        sql: "SELECT COUNT(*) as total FROM nodes",
        dataSources: ["nodes"],
      });

      await sqlQuery.executeQuery();

      expect(sqlQuery.getSingleValue.value).toBe(500);
    });

    it("should return null for empty results", async () => {
      mockExecuteQuery.mockResolvedValueOnce([]);

      const sqlQuery = useSqlQuery({
        sql: "SELECT COUNT(*) as total FROM nodes",
        dataSources: ["nodes"],
      });

      await sqlQuery.executeQuery();

      expect(sqlQuery.getSingleValue.value).toBeNull();
    });
  });

  describe("cache management", () => {
    it("should clear cache", async () => {
      const sqlQuery = useSqlQuery({
        sql: "SELECT COUNT(*) as count FROM nodes",
        dataSources: ["nodes"],
      });

      // Execute query to populate cache
      await sqlQuery.executeQuery();
      expect(mockExecuteQuery).toHaveBeenCalledTimes(1);

      // Execute again - should use cache
      await sqlQuery.executeQuery();
      expect(mockExecuteQuery).toHaveBeenCalledTimes(1);

      // Clear cache and execute again
      sqlQuery.clearCache();
      await sqlQuery.executeQuery();
      expect(mockExecuteQuery).toHaveBeenCalledTimes(2);
    });
  });

  describe("retry functionality", () => {
    it("should retry query and clear cache", async () => {
      const sqlQuery = useSqlQuery({
        sql: "SELECT COUNT(*) as count FROM nodes",
        dataSources: ["nodes"],
      });

      // Initial execution
      await sqlQuery.executeQuery();
      expect(mockExecuteQuery).toHaveBeenCalledTimes(1);

      // Retry should clear cache and re-execute
      await sqlQuery.retry();
      expect(mockExecuteQuery).toHaveBeenCalledTimes(2);
    });
  });
});
