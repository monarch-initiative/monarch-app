import { ref, type Ref } from "vue";
import * as duckdb from "@duckdb/duckdb-wasm";

export interface DuckDBConfig {
  wasmUrl?: string;
  workerUrl?: string;
}

export interface QueryResult {
  data: Record<string, any>[];
  columns: string[];
  rowCount: number;
}

/**
 * Composable for DuckDB WASM integration Provides basic database initialization
 * and parquet file loading
 */
export function useDuckDB(config: DuckDBConfig = {}) {
  const db: Ref<duckdb.AsyncDuckDB | null> = ref(null);
  const connection: Ref<duckdb.AsyncDuckDBConnection | null> = ref(null);
  const isInitialized = ref(false);
  const isLoading = ref(false);
  const error: Ref<string | null> = ref(null);

  /** Process DuckDB values to convert to proper JavaScript types */
  const processValue = (value: any): any => {
    // Handle DuckDB-specific data types first
    if (value instanceof Uint32Array) {
      // For Uint32Array, take the first element which contains the actual value
      return value[0];
    }

    if (typeof value === "bigint") {
      // Convert BigInt to regular number (may lose precision for very large numbers)
      return Number(value);
    }

    if (
      value instanceof Int32Array ||
      value instanceof Float64Array ||
      value instanceof Float32Array
    ) {
      // Handle other typed arrays
      return value[0];
    }

    // Handle JSON-serialized strings (original logic)
    if (typeof value !== "string") {
      return value;
    }

    // Handle empty string case - don't convert to number
    if (value === "") {
      return value;
    }

    let processedValue = value;

    // Try multiple rounds of JSON parsing for deeply nested quotes
    try {
      // Keep parsing until we can't parse anymore or get a non-string
      while (
        typeof processedValue === "string" &&
        processedValue.startsWith('"') &&
        processedValue.endsWith('"')
      ) {
        processedValue = JSON.parse(processedValue);
      }
    } catch {
      // If JSON parsing fails at any point, continue with what we have
    }

    // Now try to convert to number if it looks numeric
    if (typeof processedValue === "string" && processedValue.trim() !== "") {
      const numValue = Number(processedValue);
      if (!isNaN(numValue)) {
        return numValue;
      }
    }

    return processedValue;
  };

  /** Initialize DuckDB instance */
  const initDB = async (): Promise<void> => {
    if (isInitialized.value) return;

    try {
      isLoading.value = true;
      error.value = null;

      // Use local WASM files served by Vite instead of CDN to avoid CORS issues
      const baseUrl = import.meta.env.BASE_URL || "/";
      const wasmUrl = config.wasmUrl || `${baseUrl}duckdb/duckdb-mvp.wasm`;
      const workerUrl =
        config.workerUrl || `${baseUrl}duckdb/duckdb-browser-mvp.worker.js`;

      const bundle = await duckdb.selectBundle({
        mvp: {
          mainModule: wasmUrl,
          mainWorker: workerUrl,
        },
        eh: {
          mainModule: wasmUrl,
          mainWorker: workerUrl,
        },
      });

      const worker = new Worker(bundle.mainWorker!);
      const logger = new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING);
      db.value = new duckdb.AsyncDuckDB(logger, worker);
      await db.value.instantiate(bundle.mainModule);

      connection.value = await db.value.connect();
      isInitialized.value = true;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to initialize DuckDB";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Load a parquet file from URL */
  const loadParquet = async (url: string, tableName: string): Promise<void> => {
    if (!connection.value || !isInitialized.value) {
      throw new Error("DuckDB not initialized");
    }

    try {
      isLoading.value = true;
      error.value = null;

      // Create table from parquet file
      const sql = `CREATE OR REPLACE TABLE ${tableName} AS SELECT * FROM read_parquet('${url}')`;
      await connection.value.query(sql);
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to load parquet file";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Load a CSV file from URL */
  const loadCSV = async (url: string, tableName: string): Promise<void> => {
    if (!connection.value || !isInitialized.value) {
      throw new Error("DuckDB not initialized");
    }

    try {
      isLoading.value = true;
      error.value = null;

      // Create table from CSV file with header detection
      const sql = `CREATE OR REPLACE TABLE ${tableName} AS SELECT * FROM read_csv_auto('${url}')`;
      await connection.value.query(sql);
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to load CSV file";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Execute a SQL query */
  const query = async (sql: string): Promise<QueryResult> => {
    if (!connection.value || !isInitialized.value) {
      throw new Error("DuckDB not initialized");
    }

    try {
      isLoading.value = true;
      error.value = null;

      const result = await connection.value.query(sql);
      const columns = result.schema.fields.map((field: any) => field.name);

      // Get raw data and process to ensure proper data types
      const rawData = result.toArray().map((row: any) => row.toJSON());

      // Post-process to convert JSON-serialized values to proper types
      const data = rawData.map((row: any) => {
        const processedRow: Record<string, any> = {};
        Object.entries(row).forEach(([key, value]) => {
          processedRow[key] = processValue(value);
        });
        return processedRow;
      });

      return {
        data,
        columns,
        rowCount: data.length,
      };
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Query execution failed";
      error.value = errorMessage;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Clean up resources */
  const cleanup = async (): Promise<void> => {
    if (connection.value) {
      await connection.value.close();
      connection.value = null;
    }
    if (db.value) {
      await db.value.terminate();
      db.value = null;
    }
    isInitialized.value = false;
  };

  return {
    db,
    connection,
    isInitialized,
    isLoading,
    error,
    initDB,
    loadParquet,
    loadCSV,
    query,
    cleanup,
  };
}
