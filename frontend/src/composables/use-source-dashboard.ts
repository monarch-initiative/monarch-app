import { computed, reactive, type ShallowRef } from "vue";
import { useRoute } from "vue-router";
import { RESOURCE_NAME_MAP } from "@/config/resourceNames";
import { useParam, stringParam, type Param } from "@/composables/use-param";

/** number param that omits the default value from the URL */
const defaultNumberParam = (defaultValue: number): Param<number> => ({
  parse: (value) => Number(value) || defaultValue,
  stringify: (value) => (value === defaultValue ? "" : String(value)),
});

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

const filterKeys: (keyof SourceFilters)[] = [
  "category",
  "subjectCategory",
  "objectCategory",
  "predicate",
  "subjectTaxonLabel",
  "objectTaxonLabel",
  "knowledgeLevel",
  "agentType",
  "providedBy",
  "negated",
  "primaryKnowledgeSource",
  "search",
];

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

/** shared filter, pagination, and filter-query state synced with URL */
export const useAssociationFilters = () => {
  /** create URL-synced refs for each filter key */
  const paramRefs = {} as Record<keyof SourceFilters, ShallowRef<string>>;
  for (const key of filterKeys) {
    paramRefs[key] = useParam(key, stringParam(), "");
  }

  /** reactive filters object backed by URL-synced param refs */
  const filtersSource: Record<string, unknown> = {};
  for (const key of filterKeys) {
    filtersSource[key] = computed({
      get: () => paramRefs[key].value,
      set: (v: string) => {
        paramRefs[key].value = v;
      },
    });
  }
  const filters = reactive(filtersSource) as SourceFilters;

  const offset = useParam("offset", defaultNumberParam(0), 0);
  const limit = useParam("limit", defaultNumberParam(20), 20);

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
    filterKeys.some((key) => paramRefs[key].value !== ""),
  );

  return {
    filters,
    filterQueries,
    offset,
    limit,
    setFilter,
    clearFilters,
    hasActiveFilters,
  };
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
