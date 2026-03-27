import { computed, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { RESOURCE_NAME_MAP } from "@/config/resourceNames";

/** filter state for source dashboard */
export interface SourceFilters {
  category: string;
  subjectCategory: string;
  objectCategory: string;
  predicate: string;
  subjectTaxonLabel: string;
  objectTaxonLabel: string;
  knowledgeLevel: string;
  agentType: string;
  providedBy: string;
  negated: string;
  primaryKnowledgeSource: string;
  search: string;
}

export const emptyFilters = (): SourceFilters => ({
  category: "",
  subjectCategory: "",
  objectCategory: "",
  predicate: "",
  subjectTaxonLabel: "",
  objectTaxonLabel: "",
  knowledgeLevel: "",
  agentType: "",
  providedBy: "",
  negated: "",
  primaryKnowledgeSource: "",
  search: "",
});

/** build Solr filter_queries array from active filters */
const buildFilterQueries = (filters: SourceFilters): string[] => {
  const fqs: string[] = [];
  if (filters.category) fqs.push(`category:"${filters.category}"`);
  if (filters.subjectCategory)
    fqs.push(`subject_category:"${filters.subjectCategory}"`);
  if (filters.objectCategory)
    fqs.push(`object_category:"${filters.objectCategory}"`);
  if (filters.predicate) fqs.push(`predicate:"${filters.predicate}"`);
  if (filters.subjectTaxonLabel)
    fqs.push(`subject_taxon_label:"${filters.subjectTaxonLabel}"`);
  if (filters.objectTaxonLabel)
    fqs.push(`object_taxon_label:"${filters.objectTaxonLabel}"`);
  if (filters.knowledgeLevel)
    fqs.push(`knowledge_level:"${filters.knowledgeLevel}"`);
  if (filters.agentType) fqs.push(`agent_type:"${filters.agentType}"`);
  if (filters.providedBy) fqs.push(`provided_by:"${filters.providedBy}"`);
  if (filters.negated) fqs.push(`negated:${filters.negated}`);
  if (filters.primaryKnowledgeSource)
    fqs.push(`primary_knowledge_source:"${filters.primaryKnowledgeSource}"`);
  return fqs;
};

/** shared filter, pagination, and filter-query state (no route dependency) */
export const useAssociationFilters = () => {
  const filters = reactive<SourceFilters>(emptyFilters());
  const offset = ref(0);
  const limit = ref(20);

  const filterQueries = computed(() => buildFilterQueries(filters));

  const setFilter = (key: keyof SourceFilters, value: string) => {
    filters[key] = value;
    offset.value = 0;
  };

  const clearFilters = () => {
    Object.assign(filters, emptyFilters());
    offset.value = 0;
  };

  const hasActiveFilters = computed(() =>
    Object.values(filters).some((v) => v !== ""),
  );

  return { filters, filterQueries, offset, limit, setFilter, clearFilters, hasActiveFilters };
};

/** composable for source-specific dashboard pages (reads infores from route) */
export const useSourceDashboard = () => {
  const route = useRoute();

  const inforesId = computed(() => `infores:${route.params.infores as string}`);

  const sourceName = computed(() => {
    const key = ((route.params.infores as string) || "").toUpperCase();
    return RESOURCE_NAME_MAP[key] || key || "Unknown Source";
  });

  const {
    filters,
    filterQueries,
    offset,
    limit,
    setFilter,
    clearFilters,
    hasActiveFilters,
  } = useAssociationFilters();

  return {
    inforesId,
    sourceName,
    filters,
    filterQueries,
    offset,
    limit,
    setFilter,
    clearFilters,
    hasActiveFilters,
  };
};
