import { computed, ref, type Ref } from "vue";
import { getLatestKGReleaseDate, getKGSourceUrl } from "@/api/kg-version";
import { useDuckDB } from "./use-duckdb";

export interface DataSourceConfig {
  name: string;
  url: string;
  description?: string;
  baseUrl?: string;
  format?: 'parquet' | 'csv';
}

export interface DataSource extends DataSourceConfig {
  isLoaded: boolean;
  loadError?: string;
  lastLoaded?: Date;
}

/**
 * Composable for managing KG data sources and parquet files Provides
 * registration, loading, and querying of data sources
 */
export function useKGData() {
  const dataSources: Ref<Map<string, DataSource>> = ref(new Map());
  const isLoading = ref(false);
  const error: Ref<string | null> = ref(null);
  const kgVersion = ref<string>("");
  const kgSourceUrl = ref<string>("");

  // Initialize DuckDB instance
  const duckDB = useDuckDB();

  /** Initialize the KG data system */
  const init = async (): Promise<void> => {
    try {
      isLoading.value = true;
      error.value = null;

      // Initialize DuckDB
      await duckDB.initDB();

      // Get current KG version and source URL
      await fetchKGVersion();
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to initialize KG data";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Fetch current KG version and source URL */
  const fetchKGVersion = async (): Promise<void> => {
    try {
      // Get KG version and source URL from API
      const version = await getLatestKGReleaseDate();
      const sourceUrl = await getKGSourceUrl();
      
      // Check if API returned "unknown" or invalid data
      if (version === "unknown" || sourceUrl === "unknown" || !version || !sourceUrl) {
        throw new Error("API returned unknown or invalid data");
      }
      
      kgVersion.value = version;
      // Use the source URL directly from the API (includes full path)
      kgSourceUrl.value = sourceUrl.endsWith('/') ? sourceUrl.slice(0, -1) : sourceUrl;
    } catch (err) {
      // Fallback to latest dev version if API fails or returns "unknown"
      kgVersion.value = "latest";
      kgSourceUrl.value = "https://data.monarchinitiative.org/monarch-kg-dev/latest";
    }
  };
 
  /** Register a data source */
  const registerDataSource = (config: DataSourceConfig): void => {
    const source: DataSource = {
      ...config,
      baseUrl: config.baseUrl || kgSourceUrl.value,
      isLoaded: false,
    };

    dataSources.value.set(config.name, source);
  };

  /** Get a registered data source */
  const getDataSource = (name: string): DataSource | undefined => {
    return dataSources.value.get(name);
  };

  /** Load a data source (parquet file) into DuckDB */
  const loadDataSource = async (name: string): Promise<void> => {
    const source = dataSources.value.get(name);
    if (!source) {
      throw new Error(`Data source '${name}' not found`);
    }

    if (source.isLoaded) {
      return; // Already loaded
    }

    try {
      isLoading.value = true;
      source.loadError = undefined;

      // Construct full URL
      const fullUrl = source.baseUrl
        ? `${source.baseUrl}/${source.url}`
        : source.url;

      // Load file into DuckDB based on format
      const format = source.format || 'parquet'; // Default to parquet
      if (format === 'csv') {
        await duckDB.loadCSV(fullUrl, name);
      } else {
        await duckDB.loadParquet(fullUrl, name);
      }

      // Update source status
      source.isLoaded = true;
      source.lastLoaded = new Date();
      dataSources.value.set(name, source);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load data source";
      source.loadError = errorMessage;
      dataSources.value.set(name, source);
      
      // Don't throw DuckDB initialization errors - let them be handled silently
      if (errorMessage.includes("DuckDB not initialized")) {
        return;
      }
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Execute SQL query on loaded data sources */
  const executeQuery = async (
    sql: string,
    requiredSources: string[] = [],
  ): Promise<any[]> => {
    try {
      isLoading.value = true;
      error.value = null;

      // Ensure required data sources are loaded
      for (const sourceName of requiredSources) {
        await loadDataSource(sourceName);
      }

      // Execute query
      const result = await duckDB.query(sql);
      return result.data;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Query execution failed";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /** Get all registered data sources */
  const getAllDataSources = computed(() => {
    return Array.from(dataSources.value.values());
  });

  /** Get loaded data sources */
  const getLoadedDataSources = computed(() => {
    return getAllDataSources.value.filter((source) => source.isLoaded);
  });

  /** Check if a data source is loaded */
  const isDataSourceLoaded = (name: string): boolean => {
    const source = dataSources.value.get(name);
    return source?.isLoaded ?? false;
  };

  /** Clear all data sources */
  const clearDataSources = (): void => {
    dataSources.value.clear();
  };

  /** Cleanup resources */
  const cleanup = async (): Promise<void> => {
    clearDataSources();
    await duckDB.cleanup();
  };

  return {
    // State
    dataSources,
    isLoading,
    error,
    kgVersion,
    kgSourceUrl,

    // Actions
    init,
    registerDataSource,
    getDataSource,
    loadDataSource,
    executeQuery,
    clearDataSources,
    cleanup,

    // Computed
    getAllDataSources,
    getLoadedDataSources,
    isDataSourceLoaded,
  };
}
