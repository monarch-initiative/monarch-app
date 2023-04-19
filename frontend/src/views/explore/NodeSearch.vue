<!--
  node search tab on explore page

  search for nodes in knowledge graph
-->

<template>
  <AppWrapper tag="AppSection" :wrap="$route.name !== 'Home'">
    <!-- search box -->
    <AppSelectAutocomplete
      :model-value="search"
      name="Node search"
      placeholder="Search for a gene, disease, phenotype, etc."
      :options="getAutocomplete"
      @focus="onFocus"
      @change="onChange"
      @delete="onDelete"
    />

    <!-- filters -->
    <AppFlex v-if="Object.keys(availableFilters).length">
      <template v-for="(filter, name, index) in availableFilters" :key="index">
        <AppSelectMulti
          v-if="filter.length"
          v-model="activeFilters[name]"
          v-tooltip="`${startCase(name)} filter`"
          :name="`${name}`"
          :options="availableFilters[name]"
          :show-counts="showCounts"
          @change="onFilterChange"
        />
      </template>
    </AppFlex>
  </AppWrapper>

  <AppSection v-if="$route.name !== 'Home'">
    <!-- status -->
    <AppStatus v-if="isLoading" code="loading">Loading results</AppStatus>
    <AppStatus v-else-if="isError" code="error"
      >Error loading results</AppStatus
    >
    <AppStatus v-else-if="!results.results.length" code="warning"
      >No results</AppStatus
    >

    <!-- results -->
    <AppFlex
      v-for="(result, index) in results.results"
      :key="index"
      direction="col"
      gap="small"
      h-align="stretch"
    >
      <div class="title">
        <AppIcon
          v-tooltip="startCase(result.category)"
          :icon="`category-${kebabCase(result.category)}`"
          class="type"
        />
        <AppLink
          :to="`/${kebabCase(result.category)}/${result.id}`"
          class="name"
        >
          <span v-html="result.highlight"></span>
        </AppLink>
        <AppButton
          v-tooltip="'Node ID (click to copy)'"
          class="id"
          :text="result.id"
          icon="hashtag"
          design="small"
          :copy="true"
          color="secondary"
        />
      </div>
      <p class="description truncate-3" tabindex="0">
        {{ result.description || "No description available" }}
      </p>
      <p v-if="result.altNames?.length" class="names truncate-1" tabindex="0">
        {{ result.altNames.join(" &nbsp; ") }}
      </p>
      <p v-if="result.altIds?.length" class="ids truncate-1" tabindex="0">
        {{ result.altIds.join(" &nbsp; ") }}
      </p>
    </AppFlex>

    <!-- results nav -->
    <AppFlex v-if="results.results.length" direction="col">
      <div>
        <strong>{{ from + 1 }}</strong> to <strong>{{ to + 1 }}</strong> of
        <strong>{{ results.count }}</strong> results
      </div>
      <AppFlex gap="small">
        <template v-for="(list, index) of pages" :key="index">
          <button
            v-for="pageNumber of list"
            :key="pageNumber"
            v-tooltip="`Go to page ${pageNumber + 1} of results`"
            class="page-button"
            :disabled="pageNumber === page"
            @click="page = pageNumber"
          >
            {{ pageNumber + 1 }}
          </button>
          <span v-if="index !== pages.length - 1">...</span>
        </template>
      </AppFlex>
    </AppFlex>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { groupBy, isEqual, kebabCase, sortBy, startCase, uniq } from "lodash";
import { filtersToQuery } from "@/api/facets";
import type { SearchResults } from "@/api/node-search";
import { getAutocompleteResults, getSearchResults } from "@/api/node-search";
import type { Options as AutocompleteOptions } from "@/components/AppSelectAutocomplete.vue";
import AppSelectAutocomplete from "@/components/AppSelectAutocomplete.vue";
import type { Options as MultiOptions } from "@/components/AppSelectMulti.vue";
import AppSelectMulti from "@/components/AppSelectMulti.vue";
import AppWrapper from "@/components/AppWrapper.vue";
import { addEntry, deleteEntry, history } from "@/global/history";
import { appTitle } from "@/global/meta";
import { useQuery } from "@/util/composables";

/** Route info */
const router = useRouter();
const route = useRoute();

/** Submitted search text */
const search = ref(String(route.query.search || ""));
/** Current page number */
const page = ref(0);
/** Results per page */
const perPage = ref(10);
/** Filters (facets) for search */
const availableFilters = ref<Record<string, MultiOptions>>({});
const activeFilters = ref<Record<string, MultiOptions>>({});

/** When user focuses text box */
async function onFocus() {
  /** Navigate to explore page */
  await router.push({ ...route, name: "Explore" });
  /** Refocus box */
  document?.querySelector("input")?.focus();
}

/** When user "submits" text box */
function onChange(value: string) {
  search.value = value;
  page.value = 0;
}

/** When user deletes entry in textbox */
function onDelete(value: string) {
  deleteEntry(value);
}

/** When user changes active filters */
function onFilterChange() {
  page.value = 0;
  getResults(false);
}

/** Get autocomplete results */
async function getAutocomplete(search: string): Promise<AutocompleteOptions> {
  /** If something typed in, get autocomplete options from backend */
  if (search.trim()) return await getAutocompleteResults(search);

  /**
   * Otherwise, if search box focused and nothing typed in, show some useful
   * entries
   */

  /** Show top N entries in each category */
  const top = 5;

  /** Recent searches */
  const recent = uniq([...history.value].reverse())
    .slice(0, top)
    .map((search) => ({
      name: search,
      icon: "clock-rotate-left",
      tooltip: "One of your recent node searches",
    }));

  /** Most popular searches */
  const popular = sortBy(
    Object.entries(groupBy(history.value)).map(([search, matches]) => ({
      search,
      count: matches.length,
    })),
    "count"
  )
    .filter(({ count }) => count >= 3)
    .reverse()
    .slice(0, top)
    .map(({ search }) => ({
      name: search,
      icon: "person-running",
      tooltip: "One of your frequent node searches",
    }));

  /** Example searches */
  const examples = [
    "Marfan syndrome",
    "SSH",
    "Multicystic kidney dysplasia",
  ].map((search) => ({
    name: search,
    icon: "lightbulb",
    tooltip: "Example search",
  }));

  return [...recent, ...popular, ...examples];
}

/** Get search results */
const {
  query: getResults,
  data: results,
  isLoading,
  isError,
} = useQuery(
  async function (
    /**
     * Whether to perform "fresh" search, without filters/pagination/etc. true
     * when search text changes, false when filters/pagination/etc change.
     */
    fresh: boolean
  ): Promise<SearchResults> {
    /** Get results from api */
    const response = await getSearchResults(
      search.value,
      fresh ? undefined : filtersToQuery(availableFilters.value),
      fresh ? undefined : filtersToQuery(activeFilters.value),
      fresh ? undefined : from.value
    );

    return response;
  },

  /** Default value */
  { count: 0, results: [], facets: {} },

  /** On success */
  (response, [fresh]) => {
    /** Update filters from facets returned from api, if a "fresh" search */
    if (fresh) {
      availableFilters.value = { ...response.facets };
      activeFilters.value = { ...response.facets };
    }

    /** Add search to history */
    addEntry(search.value);
  }
);

/** "x of n" pages */
const from = computed((): number => page.value * perPage.value);
const to = computed(
  (): number => from.value + results.value.results.length - 1
);

/** Pages of results */
const pages = computed((): Array<Array<number>> => {
  /** Get full list of pages */
  const pages = Array(Math.ceil(results.value.count / perPage.value))
    .fill(0)
    .map((_, i) => i);

  /** Make shorter pages list */
  let list = [
    /** First few pages */
    0,
    1,
    2,
    /** Current few pages */
    page.value - 1,
    page.value,
    page.value + 1,
    /** Last few pages */
    pages.length - 3,
    pages.length - 2,
    pages.length - 1,
  ];

  /** Sort, deduplicate, and clamp list */
  list.sort((a, b) => a - b);
  list = uniq(list).filter((page) => page >= 0 && page <= pages.length - 1);

  /** Split into sub lists where page numbers are not sequential */
  const splitList: Array<Array<number>> = [[]];
  for (let index = 0; index < list.length; index++) {
    if (list[index - 1] && list[index] - list[index - 1] > 1)
      splitList.push([]);
    splitList[splitList.length - 1].push(list[index]);
  }

  return splitList;
});

/** When route changes */
watch(
  () => route.query.search,
  async () => {
    /** Update search text from route */
    search.value = String(route.query.search || "");
    /** Update document title */
    if (search.value) appTitle.value = [`"${search.value}"`];
    /** Refetch search */
    await getResults(true);
  },
  { immediate: true, flush: "post" }
);

/** When search changes */
watch(search, async () => {
  /** Update url */
  const query: Record<string, string> = {};
  if (search.value) query.search = search.value;
  await router.push({ ...route, name: "Explore", query });
});

/** When start page changes */
watch(from, () => getResults(false));

/**
 * Hide counts in filter dropdowns if any filtering being done. see
 * https://github.com/monarch-initiative/monarch-ui-new/issues/87
 */
const showCounts = computed(() =>
  isEqual(activeFilters.value, availableFilters.value)
);
</script>

<style lang="scss" scoped>
.title {
  display: flex;
  align-items: center;
  gap: 15px;
  text-align: left;
}

.type {
  font-size: 2rem;
  flex-shrink: 0;
  flex-grow: 0;
}

.name {
  flex-grow: 1;
}

.id {
  font-size: 0.9rem;
}

@media (max-width: 600px) {
  .title {
    flex-direction: column;
    align-items: flex-start;
  }
}

.names,
.ids {
  text-align: left;
  font-size: 0.9rem;
  color: $dark-gray;

  span {
    width: 100%;
  }
}

.page-button {
  height: 30px;
  padding: 0 3px;
  color: $theme-dark;
  border-radius: $rounded;
  transition: box-shadow $fast;

  &:hover {
    box-shadow: $outline;
  }
}
</style>

<style>
.hilite {
  font-style: normal;
  font-weight: 600;
}
</style>
