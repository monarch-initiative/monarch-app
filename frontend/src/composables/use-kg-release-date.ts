// src/composables/use-latest-kg-release-date.ts
import { getLatestKGReleaseDate } from "@/api/kg-version";
import { useQuery } from "@/composables/use-query";

/**
 * Composable hook to fetch and manage the latest Monarch Knowledge Graph
 * release info.
 *
 * @returns {latestRelease:
 *   isLoading: boolean,
 *   latestReleaseDate: string,
 *   isError: boolean,
 *   fetchRelease: () => void}
 */
export function useLatestKGReleaseDate() {
  const {
    query: fetchReleaseDate,
    data: latestReleaseDate,
    isLoading,
    isError,
  } = useQuery<string, []>(() => getLatestKGReleaseDate(), "");

  return {
    latestReleaseDate,
    isLoading,
    isError,
    fetchReleaseDate,
  };
}
