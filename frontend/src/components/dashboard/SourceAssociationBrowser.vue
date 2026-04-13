<template>
  <div class="association-browser">
    <!-- Mobile sidebar toggle -->
    <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen">
      {{ sidebarOpen ? "Hide Filters" : "Show Filters" }}
    </button>

    <div class="browser-layout">
      <!-- Filter sidebar -->
      <aside v-show="sidebarOpen" class="filter-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">Filters</span>
          <button
            v-if="hasActiveFilters"
            class="clear-all-link"
            @click="clearFilters"
          >
            Clear all
          </button>
        </div>

        <!-- Search -->
        <div class="sidebar-section">
          <label for="filter-search">Search</label>
          <input
            id="filter-search"
            :value="filters.search"
            type="text"
            placeholder="Search associations..."
            @input="onSearchInput(($event.target as HTMLInputElement).value)"
          />
        </div>

        <!-- Data-driven facet link lists -->
        <div
          v-for="facet in facetConfigs"
          :key="facet.filterKey"
          class="sidebar-section"
        >
          <span class="facet-heading">{{ facet.label }}</span>
          <ul v-if="facet.values.value.length" class="facet-list">
            <li
              v-for="f in getVisibleValues(facet.filterKey, facet.values.value)"
              :key="f.label"
            >
              <button
                class="facet-link"
                :class="{
                  'facet-link--active': filters[facet.filterKey] === f.label,
                }"
                @click="
                  setFilter(
                    facet.filterKey,
                    filters[facet.filterKey] === f.label ? '' : f.label,
                  )
                "
              >
                <span
                  v-tooltip="facet.formatter(f.label)"
                  class="facet-label"
                  >{{ facet.formatter(f.label) }}</span
                >
                <span class="facet-count">{{ f.count?.toLocaleString() }}</span>
              </button>
            </li>
          </ul>
          <button
            v-if="facet.values.value.length > FACET_COLLAPSE_LIMIT"
            class="facet-toggle"
            @click="
              expandedFacets[facet.filterKey] = !expandedFacets[facet.filterKey]
            "
          >
            {{
              expandedFacets[facet.filterKey]
                ? "Show less \u25B2"
                : `Show ${facet.values.value.length - FACET_COLLAPSE_LIMIT} more \u25BC`
            }}
          </button>
        </div>
      </aside>

      <!-- Content area -->
      <div class="content-area">
        <!-- Total count -->
        <div v-if="results" class="total-count">
          {{ results.total.toLocaleString() }} association{{
            results.total === 1 ? "" : "s"
          }}
        </div>

        <!-- Active filter pills -->
        <div v-if="hasActiveFilters" class="active-filters">
          <span class="active-filters-label">Active filters:</span>
          <template v-for="facet in facetConfigs" :key="facet.filterKey">
            <button
              v-if="filters[facet.filterKey]"
              class="filter-pill"
              @click="setFilter(facet.filterKey, '')"
            >
              {{ facet.label }}:
              {{ facet.formatter(filters[facet.filterKey]) }} &times;
            </button>
          </template>
          <button
            v-if="filters.search"
            class="filter-pill"
            @click="setFilter('search', '')"
          >
            Search: "{{ filters.search }}" &times;
          </button>
        </div>

        <!-- Loading / Error / Results -->
        <AppStatus v-if="isLoading && !results" code="loading"
          >Loading associations...</AppStatus
        >
        <AppStatus v-else-if="isError" code="error">
          Error loading associations.
          <button class="retry-button" @click="fetchAssociations">Retry</button>
        </AppStatus>

        <template v-else-if="results">
          <!-- Association table -->
          <AppTable
            id="source-associations"
            :cols="cols"
            :rows="results.items"
            :sort="sort"
            :total="results.total"
            @update:sort="onSortChange"
          >
            <template #subject="{ row }">
              <div class="badgeColumn">
                <AppNodeBadge
                  :node="{
                    id: row.subject,
                    category: row.subject_category || '',
                    name:
                      getHighlight(row, 'subject_label') ||
                      row.subject_label ||
                      row.subject,
                  }"
                  :is-link="true"
                  :icon="true"
                  :highlight="true"
                />
                <AppNodeText
                  v-if="
                    getAncestorHighlight(
                      row,
                      'subject_closure_label',
                      'subject_label',
                    )
                  "
                  :text="`Ancestor: ${getAncestorHighlight(row, 'subject_closure_label', 'subject_label')}`"
                  class="text-sm"
                  :highlight="true"
                />
              </div>
            </template>

            <template #predicate="{ row }">
              <AppPredicateBadge
                :association="row"
                :arrows="true"
                :highlight="true"
              />
            </template>

            <template #object="{ row }">
              <div class="badgeColumn">
                <AppNodeBadge
                  :node="{
                    id: row.object,
                    category: row.object_category || '',
                    name:
                      getHighlight(row, 'object_label') ||
                      row.object_label ||
                      row.object,
                  }"
                  :is-link="true"
                  :icon="true"
                  :highlight="true"
                />
                <AppNodeText
                  v-if="
                    getAncestorHighlight(
                      row,
                      'object_closure_label',
                      'object_label',
                    )
                  "
                  :text="`Ancestor: ${getAncestorHighlight(row, 'object_closure_label', 'object_label')}`"
                  class="text-sm"
                  :highlight="true"
                />
              </div>
            </template>

            <template #details="{ row }">
              <AppButton
                v-tooltip="'View association details'"
                design="small"
                icon="circle-info"
                @click="openDetails(row)"
              />
            </template>
          </AppTable>

          <!-- Association detail modal -->
          <AppModal v-model="showModal" label="Association Details">
            <div v-if="selectedAssociation" class="detail-modal">
              <h3>Association Details</h3>

              <!-- Triple display -->
              <div class="detail-triple">
                <AppNodeBadge
                  :node="{
                    id: selectedAssociation.subject,
                    name: selectedAssociation.subject_label,
                    category: selectedAssociation.subject_category,
                  }"
                  :name="
                    selectedAssociation.subject_label ||
                    selectedAssociation.subject
                  "
                  :is-link="true"
                  :icon="true"
                />
                <AppPredicateBadge
                  :association="selectedAssociation"
                  :arrows="true"
                />
                <AppNodeBadge
                  :node="{
                    id: selectedAssociation.object,
                    name: selectedAssociation.object_label,
                    category: selectedAssociation.object_category,
                  }"
                  :name="
                    selectedAssociation.object_label ||
                    selectedAssociation.object
                  "
                  :is-link="true"
                  :icon="true"
                />
              </div>

              <!-- Properties table -->
              <table class="detail-table">
                <tbody>
                  <tr v-for="prop in associationProperties" :key="prop.label">
                    <th>{{ prop.label }}</th>
                    <td>
                      <template v-if="prop.isLink">
                        <a
                          v-for="(link, i) in prop.links"
                          :key="i"
                          :href="link.url"
                          target="_blank"
                          rel="noopener"
                          class="detail-link"
                        >
                          {{ link.text }}
                        </a>
                      </template>
                      <span
                        v-else
                        :class="{
                          'negated-value': prop.isNegated,
                          'pre-wrap': prop.preWrap,
                        }"
                      >
                        {{ prop.value }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </AppModal>

          <!-- Bottom pagination -->
          <TheTableControls
            class="bottom-pagination"
            :rows="results.items"
            :per-page="limit"
            :start="offset"
            :total="results.total"
            :show-controls="true"
            :show-download="false"
            @update:per-page="onPerPageChange"
            @update:start="onStartChange"
          />
        </template>

        <div v-if="isLoading && results" class="loading-overlay">
          <AppStatus code="loading">Updating...</AppStatus>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, type ComputedRef } from "vue";
import type { Association, AssociationResults, FacetValue } from "@/api/model";
import { getSourceAssociations } from "@/api/source-associations";
import AppModal from "@/components/AppModal.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppNodeText from "@/components/AppNodeText.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import AppStatus from "@/components/AppStatus.vue";
import AppTable, { type Cols, type Sort } from "@/components/AppTable.vue";
import TheTableControls from "@/components/TheTableContols.vue";
import type { SourceFilters } from "@/composables/use-source-dashboard";

type Props = {
  inforesId?: string;
  filters: SourceFilters;
  filterQueries: string[];
  offset: number;
  limit: number;
  hasActiveFilters: boolean;
  setFilter: (key: keyof SourceFilters, value: string) => void;
  clearFilters: () => void;
};

const props = withDefaults(defineProps<Props>(), {
  inforesId: "",
});

const emit = defineEmits<{
  "update:offset": [number];
  "update:limit": [number];
}>();

/** Get a highlighted field value from an association's Solr highlighting data */
const getHighlight = (row: Association, field: string): string | undefined => {
  return (row as any).highlighting?.[field]?.[0];
};

/** Strip HTML tags for plain-text comparison */
const stripTags = (html: string) => html.replace(/<[^>]*>/g, "");

/** Get ancestor highlight only if it differs from the entity label */
const getAncestorHighlight = (
  row: Association,
  closureField: string,
  labelField: "subject_label" | "object_label",
): string | undefined => {
  const hl = getHighlight(row, closureField);
  if (!hl) return undefined;
  const plain = stripTags(hl);
  const label = (row as any)[labelField] || "";
  return plain === label ? undefined : hl;
};

const isLoading = ref(false);
const isError = ref(false);
const results = ref<AssociationResults | null>(null);
const sort = ref<Sort>(null);
let searchDebounce: ReturnType<typeof setTimeout> | null = null;

/** facet fields we request from the API */
const facetFields = [
  "category",
  "subject_category",
  "object_category",
  "predicate",
  "subject_taxon_label",
  "object_taxon_label",
  "knowledge_level",
  "agent_type",
  "provided_by",
  "negated",
  "primary_knowledge_source",
];

/** extract facet values for a given field from the results */
const getFacetValues = (field: string): FacetValue[] =>
  results.value?.facet_fields?.find((f) => f.label === field)?.facet_values ??
  [];

const categoryFacets = computed(() => getFacetValues("category"));
const subjectCategoryFacets = computed(() =>
  getFacetValues("subject_category"),
);
const objectCategoryFacets = computed(() => getFacetValues("object_category"));
const predicateFacets = computed(() => getFacetValues("predicate"));
const subjectTaxonFacets = computed(() =>
  getFacetValues("subject_taxon_label"),
);
const objectTaxonFacets = computed(() => getFacetValues("object_taxon_label"));
const knowledgeLevelFacets = computed(() => getFacetValues("knowledge_level"));
const agentTypeFacets = computed(() => getFacetValues("agent_type"));
const providedByFacets = computed(() => getFacetValues("provided_by"));
const negatedFacets = computed(() => getFacetValues("negated"));
const primaryKnowledgeSourceFacets = computed(() =>
  getFacetValues("primary_knowledge_source"),
);

/** format biolink categories for display */
const formatCategory = (value: string) =>
  value.replace("biolink:", "").replace(/_/g, " ");

/** identity formatter (no transformation) */
const identity = (value: string) => value;

/** sidebar open state (for mobile toggle) */
const sidebarOpen = ref(true);

/** how many facet values to show before "Show more" */
const FACET_COLLAPSE_LIMIT = 5;

/** tracks which facets are expanded past the collapse limit */
const expandedFacets = reactive<Record<string, boolean>>({});

/** get visible facet values, respecting expand/collapse state */
const getVisibleValues = (key: string, values: FacetValue[]) =>
  expandedFacets[key] ? values : values.slice(0, FACET_COLLAPSE_LIMIT);

/** data-driven facet config for the sidebar */
type FacetConfig = {
  filterKey: keyof SourceFilters;
  label: string;
  values: ComputedRef<FacetValue[]>;
  formatter: (v: string) => string;
};

const facetConfigs = computed<FacetConfig[]>(() => {
  const configs: FacetConfig[] = [
    {
      filterKey: "category",
      label: "Association Type",
      values: categoryFacets,
      formatter: formatCategory,
    },
    {
      filterKey: "subjectCategory",
      label: "Subject Category",
      values: subjectCategoryFacets,
      formatter: formatCategory,
    },
    {
      filterKey: "predicate",
      label: "Predicate",
      values: predicateFacets,
      formatter: formatCategory,
    },
    {
      filterKey: "objectCategory",
      label: "Object Category",
      values: objectCategoryFacets,
      formatter: formatCategory,
    },
    {
      filterKey: "subjectTaxonLabel",
      label: "Subject Taxon",
      values: subjectTaxonFacets,
      formatter: identity,
    },
    {
      filterKey: "objectTaxonLabel",
      label: "Object Taxon",
      values: objectTaxonFacets,
      formatter: identity,
    },
    {
      filterKey: "knowledgeLevel",
      label: "Knowledge Level",
      values: knowledgeLevelFacets,
      formatter: identity,
    },
    {
      filterKey: "agentType",
      label: "Agent Type",
      values: agentTypeFacets,
      formatter: identity,
    },
    {
      filterKey: "primaryKnowledgeSource",
      label: "Source",
      values: primaryKnowledgeSourceFacets,
      formatter: identity,
    },
    {
      filterKey: "providedBy",
      label: "Provided By",
      values: providedByFacets,
      formatter: identity,
    },
    {
      filterKey: "negated",
      label: "Negated",
      values: negatedFacets,
      formatter: identity,
    },
  ];
  // When scoped to a source, hide the source facet (it's redundant)
  if (props.inforesId) {
    return configs.filter((c) => c.filterKey !== "primaryKnowledgeSource");
  }
  return configs;
});

/** table columns */
const cols: Cols<keyof Association> = [
  {
    slot: "subject",
    key: "subject_label",
    heading: "Subject",
    sortable: true,
  },
  {
    slot: "predicate",
    key: "predicate",
    heading: "Predicate",
    sortable: true,
  },
  {
    slot: "object",
    key: "object_label",
    heading: "Object",
    sortable: true,
  },
  {
    slot: "details",
    heading: "",
    width: "40px",
  },
];

/** modal state for association details */
const showModal = ref(false);
const selectedAssociation = ref<Association | null>(null);

const openDetails = (row: Association) => {
  selectedAssociation.value = row;
  showModal.value = true;
};

type DetailProperty = {
  label: string;
  value: string;
  isLink?: boolean;
  isNegated?: boolean;
  preWrap?: boolean;
  links?: { text: string; url: string }[];
};

/** extract displayable properties from the selected association */
const associationProperties = computed((): DetailProperty[] => {
  const a = selectedAssociation.value;
  if (!a) return [];
  const details: DetailProperty[] = [];

  if (a.negated != null) {
    details.push({
      label: "Negated",
      value: a.negated ? "Yes" : "No",
      isNegated: a.negated,
    });
  }
  if (a.category) {
    details.push({ label: "Category", value: formatCategory(a.category) });
  }
  if (a.subject_taxon_label || a.subject_taxon) {
    details.push({
      label: "Subject Taxon",
      value: a.subject_taxon_label || a.subject_taxon || "",
    });
  }
  if (a.object_taxon_label || a.object_taxon) {
    details.push({
      label: "Object Taxon",
      value: a.object_taxon_label || a.object_taxon || "",
    });
  }
  if (a.primary_knowledge_source) {
    details.push({
      label: "Primary Knowledge Source",
      value: a.primary_knowledge_source,
    });
  }
  if (a.aggregator_knowledge_source?.length) {
    details.push({
      label: "Aggregator Knowledge Source",
      value: a.aggregator_knowledge_source.join(", "),
    });
  }
  if (a.provided_by) {
    details.push({
      label: "Provided By",
      value: a.provided_by,
      isLink: !!a.provided_by_link?.url,
      links: a.provided_by_link?.url
        ? [
            {
              text: a.provided_by_link.id || a.provided_by,
              url: a.provided_by_link.url,
            },
          ]
        : undefined,
    });
  }
  if (a.has_evidence_links?.length) {
    details.push({
      label: "Evidence",
      value: "",
      isLink: true,
      links: a.has_evidence_links.map((e) => ({
        text: e.id || "",
        url: e.url || "",
      })),
    });
  } else if (a.has_evidence?.length) {
    details.push({ label: "Evidence", value: a.has_evidence.join(", ") });
  }
  if (a.publications_links?.length) {
    details.push({
      label: "Publications",
      value: "",
      isLink: true,
      links: a.publications_links.map((p) => ({
        text: p.id || "",
        url: p.url || "",
      })),
    });
  } else if (a.publications?.length) {
    details.push({ label: "Publications", value: a.publications.join(", ") });
  }
  if (a.supporting_text?.length) {
    const texts = Array.isArray(a.supporting_text)
      ? a.supporting_text
      : [a.supporting_text];
    details.push({
      label: "Supporting Text",
      value: texts.join("\n\n"),
      preWrap: true,
    });
  }
  if (a.frequency_qualifier_label || a.frequency_qualifier) {
    details.push({
      label: "Frequency",
      value: a.frequency_qualifier_label || a.frequency_qualifier || "",
    });
  }
  if (a.onset_qualifier_label || a.onset_qualifier) {
    details.push({
      label: "Onset",
      value: a.onset_qualifier_label || a.onset_qualifier || "",
    });
  }
  if (a.sex_qualifier_label || a.sex_qualifier) {
    details.push({
      label: "Sex",
      value: a.sex_qualifier_label || a.sex_qualifier || "",
    });
  }
  if (a.knowledge_level) {
    details.push({ label: "Knowledge Level", value: a.knowledge_level });
  }
  if (a.agent_type) {
    details.push({ label: "Agent Type", value: a.agent_type });
  }
  if (a.id) {
    details.push({ label: "Association ID", value: a.id });
  }
  return details;
});

/** fetch associations from API */
const fetchAssociations = async () => {
  isLoading.value = true;
  isError.value = false;
  try {
    results.value = await getSourceAssociations(
      props.inforesId || undefined,
      props.offset,
      props.limit,
      facetFields,
      props.filterQueries.length > 0 ? props.filterQueries : undefined,
      sort.value,
      props.filters.search || undefined,
    );
  } catch (e) {
    console.error("Error fetching source associations:", e);
    isError.value = true;
  } finally {
    isLoading.value = false;
  }
};

/** debounced search input */
const onSearchInput = (value: string) => {
  if (searchDebounce) clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    props.setFilter("search", value);
  }, 300);
};

/** pagination handlers */
const onPerPageChange = (perPage?: number) => {
  if (perPage != null) {
    emit("update:limit", perPage);
    emit("update:offset", 0);
  }
};

const onStartChange = (start?: number) => {
  if (start != null) {
    emit("update:offset", start);
  }
};

/** sort handler */
const onSortChange = (newSort?: Sort) => {
  sort.value = newSort ?? null;
};

/** watch for changes and refetch */
watch(
  () => [
    props.inforesId,
    props.offset,
    props.limit,
    props.filterQueries,
    props.filters.search,
    sort.value,
  ],
  () => fetchAssociations(),
  { immediate: true, deep: true },
);
</script>

<style lang="scss" scoped>
.association-browser {
  position: relative;
}

.sidebar-toggle {
  display: none;
  align-items: center;
  margin-bottom: 0.75rem;
  padding: 0.4rem 0.8rem;
  gap: 0.4rem;
  border: 1px solid $light-gray;
  border-radius: $rounded;
  background: $white;
  color: $off-black;
  font-size: 0.85rem;
  cursor: pointer;

  &:hover {
    background: $light-gray;
  }
}

.browser-layout {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.filter-sidebar {
  position: sticky;
  top: 1rem;
  flex-shrink: 0;
  width: 260px;
  max-height: calc(100vh - 2rem);
  padding: 0.75rem;
  overflow-y: auto;
  border: 1px solid $light-gray;
  border-radius: $rounded;
  background: $off-white;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid $light-gray;
}

.sidebar-title {
  color: $off-black;
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.clear-all-link {
  padding: 0;
  border: none;
  background: none;
  color: $theme;
  font-size: 0.8rem;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.75rem;
  gap: 0.25rem;

  label {
    color: $off-black;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
  }

  input {
    width: 100%;
    padding: 0.4rem 0.5rem;
    border: 1px solid $light-gray;
    border-radius: $rounded;
    font-size: 0.85rem;

    &:focus {
      border-color: $theme;
      outline: none;
      box-shadow: $outline;
    }
  }
}

.facet-heading {
  color: $off-black;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.facet-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.facet-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.2rem 0.4rem;
  border: none;
  border-left: 3px solid transparent;
  border-radius: 0;
  background: none;
  color: $off-black;
  font-size: 0.82rem;
  text-align: left;
  cursor: pointer;

  &:hover {
    background: $theme-light;
    color: $theme;
  }

  &--active {
    border-left-color: $theme;
    background: $theme-light;
    color: $theme;
    font-weight: 600;
  }
}

.facet-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.facet-count {
  flex-shrink: 0;
  margin-left: 0.5rem;
  color: $gray;
  font-weight: 400;
  font-size: 0.78rem;
}

.facet-toggle {
  padding: 0.15rem 0.4rem;
  border: none;
  background: none;
  color: $theme;
  font-size: 0.78rem;
  text-align: left;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

.content-area {
  position: relative;
  flex: 1;
  min-width: 0;

  :deep(td) {
    padding-top: 0.6rem;
    padding-bottom: 0.6rem;
  }
}

.bottom-pagination {
  margin-top: 1rem;
}

.total-count {
  margin-bottom: 0.75rem;
  color: $dark-gray;
  font-weight: 600;
  font-size: 1.1rem;
}

.active-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.active-filters-label {
  color: $dark-gray;
  font-size: 0.85rem;
}

.filter-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  gap: 0.3rem;
  border: none;
  border-radius: 999px;
  background: $theme-light;
  color: $theme;
  font-size: 0.8rem;
  cursor: pointer;

  &:hover {
    background: $theme-mid;
  }
}

.loading-overlay {
  display: flex;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.7);
}

.detail-modal {
  padding: 1rem;

  h3 {
    margin: 0 0 1.5rem 0;
    color: $off-black;
    font-size: 1.15rem;
  }
}

.detail-triple {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  gap: 10px 20px;
  border-radius: $rounded;
  background: $off-white;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid $light-gray;
    text-align: left;
    vertical-align: top;
  }

  th {
    width: 180px;
    color: $dark-gray;
    font-weight: 600;
    font-size: 0.85rem;
    white-space: nowrap;
  }

  td {
    color: $off-black;
    font-size: 0.9rem;
    word-break: break-word;
  }
}

.detail-link {
  display: inline-block;
  margin-right: 0.5rem;
  color: $theme;

  &:hover {
    text-decoration: underline;
  }
}

.retry-button {
  margin-left: 0.5rem;
  padding: 0.3rem 0.8rem;
  border: 1px solid currentcolor;
  border-radius: $rounded;
  background: none;
  color: inherit;
  font-size: 0.85rem;
  cursor: pointer;

  &:hover {
    background: rgba(0, 0, 0, 0.05);
  }
}

.badgeColumn {
  display: flex;
  flex-direction: column;
  gap: 0.2em;
}

.text-sm {
  color: $dark-gray;
  font-size: 0.9em;
}

.negated-value {
  color: $error;
  font-weight: 600;
}

.pre-wrap {
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .sidebar-toggle {
    display: inline-flex;
  }

  .browser-layout {
    flex-direction: column;
  }

  .filter-sidebar {
    position: static;
    width: 100%;
    max-height: none;
  }
}
</style>
