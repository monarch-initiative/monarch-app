import { describe, expect, it } from "vitest";

/**
 * Test the data processing logic for DuckDB query results
 * This isolates the value conversion logic to understand and fix the issue
 */
describe("DuckDB Data Processing", () => {
  // Helper function to simulate what we're doing in use-duckdb.ts
  const processValue = (value: any): any => {
    // Handle DuckDB-specific data types first
    if (value instanceof Uint32Array) {
      return value[0];
    }
    
    if (typeof value === 'bigint') {
      return Number(value);
    }
    
    if (value instanceof Int32Array || value instanceof Float64Array || value instanceof Float32Array) {
      return value[0];
    }

    // Handle JSON-serialized strings
    if (typeof value !== 'string') {
      return value;
    }

    // Handle empty string case - don't convert to number
    if (value === '') {
      return value;
    }

    let processedValue = value;
    
    // Try multiple rounds of JSON parsing for deeply nested quotes
    try {
      // Keep parsing until we can't parse anymore or get a non-string
      while (typeof processedValue === 'string' && 
             (processedValue.startsWith('"') && processedValue.endsWith('"'))) {
        processedValue = JSON.parse(processedValue);
      }
    } catch {
      // If JSON parsing fails at any point, continue with what we have
    }

    // Now try to convert to number if it looks numeric
    if (typeof processedValue === 'string' && processedValue.trim() !== '') {
      const numValue = Number(processedValue);
      if (!isNaN(numValue)) {
        return numValue;
      }
    }

    return processedValue;
  };

  describe("processValue function", () => {
    it("should handle regular numbers", () => {
      expect(processValue(123)).toBe(123);
      expect(processValue(0)).toBe(0);
      expect(processValue(-456)).toBe(-456);
    });

    it("should handle DuckDB Uint32Array values", () => {
      const uint32Array = new Uint32Array([3398, 0, 0, 0]);
      expect(processValue(uint32Array)).toBe(3398);
    });

    it("should handle BigInt values", () => {
      expect(processValue(17n)).toBe(17);
      expect(processValue(12345n)).toBe(12345);
    });

    it("should handle other typed arrays", () => {
      const int32Array = new Int32Array([42, 0]);
      const float64Array = new Float64Array([3.14, 0]);
      expect(processValue(int32Array)).toBe(42);
      expect(processValue(float64Array)).toBe(3.14);
    });

    it("should handle regular strings", () => {
      expect(processValue("hello")).toBe("hello");
      expect(processValue("")).toBe("");
    });

    it("should handle numeric strings", () => {
      expect(processValue("123")).toBe(123);
      expect(processValue("0")).toBe(0);
      expect(processValue("-456")).toBe(-456);
    });

    it("should handle JSON-encoded strings with quotes", () => {
      // This is what we're seeing: "\"3398\""
      expect(processValue('"3398"')).toBe(3398);
      expect(processValue('"0"')).toBe(0);
      expect(processValue('"-456"')).toBe(-456);
    });

    it("should handle double-encoded JSON strings", () => {
      // In case DuckDB is doing multiple levels of encoding
      expect(processValue('"\\"123\\""')).toBe(123);
    });

    it("should handle non-numeric JSON-encoded strings", () => {
      expect(processValue('"hello"')).toBe("hello");
      expect(processValue('"world"')).toBe("world");
    });

    it("should handle null and undefined", () => {
      expect(processValue(null)).toBe(null);
      expect(processValue(undefined)).toBe(undefined);
    });

    it("should handle boolean values", () => {
      expect(processValue(true)).toBe(true);
      expect(processValue(false)).toBe(false);
    });

    it("should handle arrays", () => {
      const arr = [1, 2, 3];
      expect(processValue(arr)).toBe(arr);
    });

    it("should handle objects", () => {
      const obj = { a: 1, b: 2 };
      expect(processValue(obj)).toBe(obj);
    });
  });

  describe("real DuckDB scenarios", () => {
    it("should process typical query result", () => {
      // Simulate what DuckDB might return
      const mockDuckDBResult = [
        { "total_nodes": '"3398"' },
        { "human_genes": '"243"' },
        { "total_edges": '"14040235"' }
      ];

      const processed = mockDuckDBResult.map(row => {
        const processedRow: Record<string, any> = {};
        Object.entries(row).forEach(([key, value]) => {
          processedRow[key] = processValue(value);
        });
        return processedRow;
      });

      expect(processed).toEqual([
        { "total_nodes": 3398 },
        { "human_genes": 243 },
        { "total_edges": 14040235 }
      ]);
    });

    it("should handle mixed data types", () => {
      const mockResult = [
        { 
          "count": '"123"',
          "name": '"gene_name"',
          "score": '"0.95"',
          "category": '"biolink:Gene"'
        }
      ];

      const processed = mockResult.map(row => {
        const processedRow: Record<string, any> = {};
        Object.entries(row).forEach(([key, value]) => {
          processedRow[key] = processValue(value);
        });
        return processedRow;
      });

      expect(processed).toEqual([
        {
          "count": 123,
          "name": "gene_name",
          "score": 0.95,
          "category": "biolink:Gene"
        }
      ]);
    });
  });
});