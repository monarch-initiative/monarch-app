import { getKnowledgeSourceFacets } from "@/api/sources";
import { useQuery } from "@/composables/use-query";

/** Composable to fetch primary and aggregator knowledge sources. */
export function useKnowledgeSources() {
  // Fetch primary knowledge sources
  const {
    query: queryPrimarySources,
    data: primarySources,
    isLoading: isLoadingPrimary,
    isError: isErrorPrimary,
  } = useQuery(() => getKnowledgeSourceFacets("primary_knowledge_source"), []);

  // Fetch aggregator knowledge sources
  const {
    query: queryAggregatorSources,
    data: aggregatorSources,
    isLoading: isLoadingAggregator,
    isError: isErrorAggregator,
  } = useQuery(
    () => getKnowledgeSourceFacets("aggregator_knowledge_source"),
    [],
  );

  // Fetch both sources
  const fetchAll = () => {
    queryPrimarySources();
    queryAggregatorSources();
  };

  return {
    primarySources,
    aggregatorSources,
    isLoadingPrimary,
    isLoadingAggregator,
    isErrorPrimary,
    isErrorAggregator,
    fetchAll,
  };
}
