import { computed, inject, ref, type Ref } from "vue";
import { useKGData } from "./use-kg-data";

export interface SqlQueryConfig {
  sql: string;
  dataSources: string[];
  autoExecute?: boolean;
  pollInterval?: number;
}

export interface SqlQueryResult {
  data: Record<string, any>[];
  columns: string[];
  rowCount: number;
  executionTime: number;
  isFromCache: boolean;
}

/**
 * Composable for executing SQL queries against KG data sources Provides
 * caching, validation, and reactive query execution
 */
export function useSqlQuery(config: SqlQueryConfig) {
  // Try to inject KG data from dashboard context first, fallback to creating new instance
  const injectedKgData = inject<ReturnType<typeof useKGData> | null>("kg-data", null);
  const kgData = injectedKgData || useKGData();

  const isLoading = ref(false);
  const error: Ref<string | null> = ref(null);
  const result: Ref<SqlQueryResult | null> = ref(null);
  const lastExecuted = ref<Date | null>(null);

  // Simple cache for query results
  const queryCache = ref(new Map<string, SqlQueryResult>());

  const { sql, dataSources, autoExecute = false, pollInterval } = config;

  /** Generate cache key for query */
  const getCacheKey = (query: string, sources: string[]): string => {
    return `${query}|${sources.sort().join(",")}`;
  };

  /** Validate SQL query for basic security */
  const validateSQL = (
    query: string,
  ): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    const upperQuery = query.toUpperCase().trim();

    // Check for dangerous operations
    const dangerousKeywords = [
      "DROP",
      "DELETE",
      "INSERT",
      "UPDATE",
      "ALTER",
      "CREATE",
      "TRUNCATE",
    ];
    for (const keyword of dangerousKeywords) {
      if (upperQuery.includes(keyword)) {
        errors.push(`Query contains potentially dangerous keyword: ${keyword}`);
      }
    }

    // Check for basic SQL structure
    if (!upperQuery.startsWith("SELECT") && !upperQuery.startsWith("WITH")) {
      errors.push("Query must start with SELECT or WITH");
    }

    // Check for minimum length
    if (query.trim().length < 10) {
      errors.push("Query appears to be too short");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  };

  /** Execute the SQL query */
  const executeQuery = async (
    overrideSQL?: string,
    overrideSources?: string[],
  ): Promise<SqlQueryResult> => {
    const queryToExecute = overrideSQL || sql;
    const sourcesToUse = overrideSources || dataSources;

    try {
      isLoading.value = true;
      error.value = null;

      // Validate query
      const validation = validateSQL(queryToExecute);
      if (!validation.isValid) {
        throw new Error(
          `SQL validation failed: ${validation.errors.join(", ")}`,
        );
      }

      // Check cache first
      const cacheKey = getCacheKey(queryToExecute, sourcesToUse);
      const cached = queryCache.value.get(cacheKey);
      if (cached) {
        result.value = { ...cached, isFromCache: true };
        return result.value;
      }

      // Execute query
      const startTime = performance.now();
      const data = await kgData.executeQuery(queryToExecute, sourcesToUse);
      const endTime = performance.now();


      // Process results
      const columns = data.length > 0 ? Object.keys(data[0]) : [];
      const queryResult: SqlQueryResult = {
        data,
        columns,
        rowCount: data.length,
        executionTime: endTime - startTime,
        isFromCache: false,
      };

      // Cache result
      queryCache.value.set(cacheKey, queryResult);

      result.value = queryResult;
      lastExecuted.value = new Date();

      return queryResult;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Query execution failed";
      error.value = errorMessage;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Clear query cache */
  const clearCache = (): void => {
    queryCache.value.clear();
  };

  /** Get a single value from query result (useful for metrics) */
  const getSingleValue = computed(() => {
    if (!result.value || result.value.data.length === 0) return null;

    const firstRow = result.value.data[0];
    const firstColumn = result.value.columns[0];
    const rawValue = firstRow[firstColumn];

    // Process the value to handle DuckDB data types
    const processValue = (value: any): any => {
      if (value instanceof Uint32Array) return value[0];
      if (typeof value === 'bigint') return Number(value);
      if (value instanceof Int32Array || value instanceof Float64Array || value instanceof Float32Array) return value[0];
      return value;
    };

    return processValue(rawValue);
  });

  /** Check if query should be automatically executed */
  const shouldAutoExecute = computed(() => {
    return autoExecute && !isLoading.value && !result.value;
  });

  /** Retry the last query */
  const retry = async (): Promise<void> => {
    if (result.value) {
      // Clear the cached result and re-execute
      const cacheKey = getCacheKey(sql, dataSources);
      queryCache.value.delete(cacheKey);
    }
    await executeQuery();
  };

  // Auto-execute if configured
  if (shouldAutoExecute.value) {
    executeQuery().catch((err) => {
      console.error("Auto-execute failed:", err);
    });
  }

  // Set up polling if configured
  let pollTimer: number | undefined;
  if (pollInterval && pollInterval > 0) {
    pollTimer = window.setInterval(() => {
      if (!isLoading.value) {
        // Clear cache and re-execute
        const cacheKey = getCacheKey(sql, dataSources);
        queryCache.value.delete(cacheKey);
        executeQuery().catch((err) => {
          console.error("Polling execution failed:", err);
        });
      }
    }, pollInterval);
  }

  // Cleanup polling on unmount
  const cleanup = (): void => {
    if (pollTimer) {
      clearInterval(pollTimer);
    }
  };

  return {
    // State
    isLoading,
    error,
    result,
    lastExecuted,

    // Computed
    getSingleValue,
    shouldAutoExecute,

    // Actions
    executeQuery,
    retry,
    clearCache,
    cleanup,
    validateSQL,
  };
}
