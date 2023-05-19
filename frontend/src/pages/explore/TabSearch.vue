<!--
  search tab on explore page

  search for nodes in knowledge graph
-->

<template>
  <AppWrapper tag="AppSection" :wrap="$route.name !== 'Home'">
    <!-- search box -->
    <AppSelectAutocomplete
      :model-value="search"
      name="Search"
      placeholder="Search for a gene, disease, phenotype, etc."
      :options="getAutocomplete"
      @focus="onFocus"
      @change="onChange"
      @delete="onDelete"
    />

    <!-- facet dropdown filters -->
    <AppFlex v-if="Object.keys(facets).length">
      <template v-for="(facet, id, index) in facets" :key="index">
        <AppSelectMulti
          v-if="Object.keys(facet.facet_values || {}).length"
          v-model="dropdownsSelected[id]"
          v-tooltip="`${facet.label} filter`"
          :name="`${facet.label}`"
          :options="dropdownsOptions[id]"
          @change="onSelectedChange"
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
    <AppStatus v-else-if="!results.items.length" code="warning"
      >No results</AppStatus
    >

    <!-- results -->
    <AppFlex
      v-for="(result, index) in results.items"
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
        <AppLink :to="`/${result.id}`" class="name">
          <span v-html="result.name"></span>
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
      <p v-if="result.synonym?.length" class="names truncate-1" tabindex="0">
        {{ result.synonym.join(" &nbsp; ") }}
      </p>
      <p v-if="result.xref?.length" class="ids truncate-1" tabindex="0">
        {{ result.xref.join(" &nbsp; ") }}
      </p>
    </AppFlex>

    <!-- results nav -->
    <AppFlex v-if="results.items.length" direction="col">
      <div>
        <strong>{{ from + 1 }}</strong> to <strong>{{ to + 1 }}</strong> of
        <strong>{{ results.total }}</strong> results
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
import { groupBy, kebabCase, mapValues, sortBy, startCase, uniq } from "lodash";
import type { SearchResults } from "@/api/model";
import { getAutocompleteResults, getSearchResults } from "@/api/search";
import type { Options as AutocompleteOptions } from "@/components/AppSelectAutocomplete.vue";
import AppSelectAutocomplete from "@/components/AppSelectAutocomplete.vue";
import type { Options as MultiOptions } from "@/components/AppSelectMulti.vue";
import AppSelectMulti from "@/components/AppSelectMulti.vue";
import AppWrapper from "@/components/AppWrapper.vue";
import { addEntry, deleteEntry, history } from "@/global/history";
import { appTitle } from "@/global/meta";
import { useQuery } from "@/util/composables";

/** route info */
const router = useRouter();
const route = useRoute();

/** submitted search text */
const search = ref(String(route.query.search || ""));
/** current page number */
const page = ref(0);
/** results per page */
const perPage = ref(10);
/** facets returned from search */
const facets = ref<NonNullable<SearchResults["facet_fields"]>>({});
/** dropdowns all options */
const dropdownsOptions = ref<{ [key: string]: MultiOptions }>({});
/** dropdowns selected options */
const dropdownsSelected = ref<{ [key: string]: MultiOptions }>({});

/** when user focuses text box */
async function onFocus() {
  /** navigate to explore page */
  await router.push({ ...route, name: "Explore" });
  /** refocus box */
  document?.querySelector("input")?.focus();
}

/** when user "submits" text box */
function onChange(value: string) {
  search.value = value;
  page.value = 0;
}

/** when user deletes entry in textbox */
function onDelete(value: string) {
  deleteEntry(value);
}

/** when user changes selected options */
function onSelectedChange() {
  page.value = 0;
  getSearch(false);
}

/** get autocomplete results */
async function getAutocomplete(search: string): Promise<AutocompleteOptions> {
  /** if something typed in, get autocomplete options from backend */
  if (search.trim())
    return (await getAutocompleteResults(search)).items.map((item) => ({
      label: item.name,
      icon: "category-" + item.category,
      tooltip: "",
    }));

  /**
   * otherwise, if search box focused and nothing is typed in yet, show some
   * useful entries
   */

  /** show top N entries in each category */
  const top = 5;

  /** recent searches */
  const recent = uniq([...history.value].reverse())
    .slice(0, top)
    .map((search) => ({
      label: search,
      icon: "clock-rotate-left",
      tooltip: "One of your recent searches",
    }));

  /** most popular searches */
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
      label: search,
      icon: "person-running",
      tooltip: "One of your frequent node searches",
    }));

  /** example searches */
  const examples = [
    "Marfan syndrome",
    "SSH",
    "Multicystic kidney dysplasia",
  ].map((search) => ({
    label: search,
    icon: "lightbulb",
    tooltip: "Example search",
  }));

  return [...recent, ...popular, ...examples];
}

/** get search results */
const {
  query: getSearch,
  data: results,
  isLoading,
  isError,
} = useQuery(
  async function (
    /**
     * whether to perform "fresh" search, without filters/pagination/etc. true
     * when search text changes, false when filters/pagination/etc change.
     */
    fresh: boolean
  ) {
    /** get results from api */
    const response = await getSearchResults(
      search.value,
      from.value,
      perPage.value,
      /** transform dropdown selected options into filters to search for */
      fresh
        ? undefined
        : mapValues(dropdownsSelected.value, (dropdown) =>
            dropdown.map((option) => option.id)
          )
    );

    return response;
  },

  /** default value */
  { total: 0, items: [], limit: 0, offset: 0 },

  /** on success */
  (response, [fresh]) => {
    /** update dropdowns from facets returned from api, if a "fresh" search */
    if (fresh) {
      facets.value = response.facet_fields || {};
      /** convert facets into dropdown options */
      const options = mapValues(response.facet_fields || {}, (facet) =>
        Object.entries(facet.facet_values || {}).map(([key, value]) => ({
          id: key,
          label: value.label,
          count: value.count,
        }))
      );
      dropdownsOptions.value = { ...options };
      dropdownsSelected.value = { ...options };
    }

    /** add search to history */
    addEntry(search.value);
  }
);

/** "x of n" pages */
const from = computed((): number => page.value * perPage.value);
const to = computed((): number => from.value + results.value.items.length - 1);

/** pages of results */
const pages = computed((): number[][] => {
  /** get full list of pages */
  const pages = Array(Math.ceil(results.value.total / perPage.value))
    .fill(0)
    .map((_, i) => i);

  /** make shorter pages list */
  let list = [
    /** first few pages */
    0,
    1,
    2,
    /** current few pages */
    page.value - 1,
    page.value,
    page.value + 1,
    /** last few pages */
    pages.length - 3,
    pages.length - 2,
    pages.length - 1,
  ];

  /** sort, deduplicate, and clamp list */
  list.sort((a, b) => a - b);
  list = uniq(list).filter((page) => page >= 0 && page <= pages.length - 1);

  /** split into sub lists where page numbers are not sequential */
  const splitList: number[][] = [[]];
  for (let index = 0; index < list.length; index++) {
    if (list[index - 1] && list[index] - list[index - 1] > 1)
      splitList.push([]);
    splitList[splitList.length - 1].push(list[index]);
  }

  return splitList;
});

/** when route changes */
watch(
  () => route.query.search,
  async () => {
    /** update search text from route */
    search.value = String(route.query.search || "");
    /** update document title */
    if (search.value) appTitle.value = [`"${search.value}"`];
    /** refetch search */
    await getSearch(true);
  },
  { immediate: true, flush: "post" }
);

/** when search changes */
watch(search, async () => {
  /** update url */
  const query: { [key: string]: string } = {};
  if (search.value) query.search = search.value;
  await router.push({ ...route, name: "Explore", query });
});

/** when start page changes */
watch(from, () => getSearch(false));
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
