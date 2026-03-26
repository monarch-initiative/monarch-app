import { computed, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { RESOURCE_NAME_MAP } from "@/config/resourceNames";

/** filter state for source dashboard */
export interface SourceFilters {
  subjectCategory: string;
  objectCategory: string;
  predicate: string;
  subjectTaxon: string;
  objectTaxon: string;
  knowledgeLevel: string;
  agentType: string;
  providedBy: string;
  negated: string;
  search: string;
}

const emptyFilters = (): SourceFilters => ({
  subjectCategory: "",
  objectCategory: "",
  predicate: "",
  subjectTaxon: "",
  objectTaxon: "",
  knowledgeLevel: "",
  agentType: "",
  providedBy: "",
  negated: "",
  search: "",
});

export const useSourceDashboard = () => {
  const route = useRoute();

  /**
   * infores ID derived from route param, e.g. "infores:omim" from
   * "/kg/sources/omim"
   */
  const inforesId = computed(() => `infores:${route.params.infores as string}`);

  /** human-readable source name from resource name map */
  const sourceName = computed(() => {
    const key = ((route.params.infores as string) || "").toUpperCase();
    return RESOURCE_NAME_MAP[key] || key || "Unknown Source";
  });

  /** shared filter state */
  const filters = reactive<SourceFilters>(emptyFilters());

  /** pagination state */
  const offset = ref(0);
  const limit = ref(20);

  /** build Solr filter_queries array from active filters */
  const filterQueries = computed(() => {
    const fqs: string[] = [];
    if (filters.subjectCategory)
      fqs.push(`subject_category:"${filters.subjectCategory}"`);
    if (filters.objectCategory)
      fqs.push(`object_category:"${filters.objectCategory}"`);
    if (filters.predicate) fqs.push(`predicate:"${filters.predicate}"`);
    if (filters.subjectTaxon)
      fqs.push(`subject_taxon_label:"${filters.subjectTaxon}"`);
    if (filters.objectTaxon)
      fqs.push(`object_taxon_label:"${filters.objectTaxon}"`);
    if (filters.knowledgeLevel)
      fqs.push(`knowledge_level:"${filters.knowledgeLevel}"`);
    if (filters.agentType) fqs.push(`agent_type:"${filters.agentType}"`);
    if (filters.providedBy) fqs.push(`provided_by:"${filters.providedBy}"`);
    if (filters.negated) fqs.push(`negated:${filters.negated}`);
    return fqs;
  });

  /** set a single filter value and reset pagination */
  const setFilter = (key: keyof SourceFilters, value: string) => {
    filters[key] = value;
    offset.value = 0;
  };

  /** clear all filters and reset pagination */
  const clearFilters = () => {
    Object.assign(filters, emptyFilters());
    offset.value = 0;
  };

  /** check if any filter is active */
  const hasActiveFilters = computed(() =>
    Object.values(filters).some((v) => v !== ""),
  );

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
