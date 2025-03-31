<template>
  <AppWrapper tag="AppSection" :wrap="true">
    <div class="help-icon-section">
      <AppSelectAutocomplete
        v-model="search"
        name="Search"
        placeholder="Gene, disease, phenotype, etc."
        :options="runGetAutocomplete"
        @change="onChange"
        @delete="onDelete"
      />
      <AppButton
        v-tooltip="'How to use'"
        class="help-icon"
        text="?"
        design="circle"
        color="secondary"
        to="how-to"
      />
    </div>

    <AppFlex v-if="facets.length">
      <template v-for="(facet, index) in facets" :key="index">
        <AppSelectMulti
          v-if="facet.facet_values && Object.keys(facet.facet_values).length"
          v-model="dropdownsSelected[facet.label]"
          v-tooltip="`<i>${startCase(facet.label)}</i> filter`"
          :name="startCase(facet.label)"
          :options="dropdownsOptions[facet.label]"
          :show-counts="true"
        />
      </template>
    </AppFlex>
  </AppWrapper>

  <AppSection v-if="true">
    <!-- status -->
    <AppStatus v-if="isLoading" code="loading">Loading results</AppStatus>
    <AppStatus v-else-if="isError" code="error"
      >Error loading results</AppStatus
    >
    <AppStatus v-else-if="!results.items.length" code="warning"
      >No results</AppStatus
    >

    {{ results.items.length }}
    <AppFlex
      v-for="(result, index) in results.items"
      :key="index"
      direction="col"
      gap="small"
      align-h="stretch"
    >
      <div class="title">
        <AppNodeBadge
          :node="result"
          :state="{ fromSearch: search }"
          class="title-name"
        />
        <AppButton
          v-if="result.in_taxon_label"
          v-tooltip="'Taxon Name'"
          class="title-taxon"
          :text="result.in_taxon_label || ''"
          icon=""
          design="small"
          :copy="true"
          color="none"
        />
        <AppButton
          v-tooltip="'Node ID (click to copy)'"
          class="title-id"
          :text="result.id"
          icon="barcode"
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
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { groupBy, mapValues, sortBy, startCase, uniq, uniqBy } from "lodash";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import { getAutocomplete, getSearch } from "@/api/search";
import AppButton from "@/components/AppButton.vue";
import AppFlex from "@/components/AppFlex.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type {
  Options as AutocompleteOptions,
  Option,
} from "@/components/AppSelectAutocomplete.vue";
import AppSelectAutocomplete from "@/components/AppSelectAutocomplete.vue";
import type { Options as MultiOptions } from "@/components/AppSelectMulti.vue";
import AppSelectMulti from "@/components/AppSelectMulti.vue";
import AppWrapper from "@/components/AppWrapper.vue";
import { useQuery } from "@/composables/use-query";
import { deleteEntry, history } from "@/global/history";

// Type for facet fields to avoid 'never' errors
interface FacetValue {
  label: string;
  count?: number;
}

interface FacetField {
  label: string;
  facet_values?: FacetValue[];
}

const router = useRouter();

const route = useRoute();
/** submitted search text */
const search = ref(String(route.query.search || ""));
/** current page number */
const page = ref(0);
/** results per page */
const perPage = ref(10);

const dropdownsPartial = ref<{ [key: string]: boolean }>({});

/** autocomplete option for viewing all/detailed results on explore page */
const viewAll: Option = {
  id: "ALL",
  label: "View all results...",
  icon: "arrow-right",
  // info: "on explore page",
  special: true,
};
onMounted(() => console.log("search", search));
/** get search results */
const {
  query: runGetSearch,
  data: results,
  isLoading,
  isError,
} = useQuery(
  async function (
    /**
     * whether to perform "fresh" search, without filters/pagination/etc. true
     * when search text changes, false when filters/pagination/etc change.
     */
    fresh: boolean,
  ) {
    /** get results from api */
    const response = await getSearch(
      search.value,
      from.value,
      perPage.value,
      /** transform dropdown selected options into filters to search for */
      fresh
        ? undefined
        : mapValues(dropdownsSelected.value, (dropdown, key) => {
            if (dropdownsPartial.value[key])
              return dropdown.map((option) => option.id);
            else return [];
          }),
    );

    return response;
  },

  /** default value */
  { total: 0, items: [], limit: 0, offset: 0 },

  /** on success */
  (response, [fresh]) => {
    /** update dropdowns from facets returned from api, if a "fresh" search */
    if (fresh) {
      facets.value = response.facet_fields || [];
      /** convert facets into dropdown options */
      const options: { [key: string]: MultiOptions } = {};
      for (const facet of facets.value) {
        options[facet.label || ""] =
          facet.facet_values?.map((facet_value) => ({
            id: facet_value.label,
            label:
              facet.label === "category"
                ? getCategoryLabel(facet_value.label)
                : startCase(facet_value.label),
            icon:
              facet.label === "category"
                ? getCategoryIcon(facet_value.label)
                : "",
            count: facet_value.count,
          })) || [];
      }

      dropdownsOptions.value = { ...options };
      dropdownsSelected.value = { ...options };
    }
  },
);
onMounted(() => {
  if (search.value) {
    runGetSearch(true);
  }
});
const facets = ref<FacetField[]>([]);
const dropdownsOptions = ref<Record<string, MultiOptions>>({});
const dropdownsSelected = ref<Record<string, MultiOptions>>({});
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
  list.sort();
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

function onDelete(value: Option) {
  deleteEntry(value);
}

function onChange(value: string | Option, originalSearch: string) {
  const query: Record<string, string> = {
    search: originalSearch,
  };

  for (const [key, options] of Object.entries(dropdownsSelected.value)) {
    query[key] = options.map((opt) => opt.id).join(",");
  }

  // router.push({ name: "KnowledgeGraphSearch", query });
}

/** get autocomplete results */
async function runGetAutocomplete(
  search: string,
): Promise<AutocompleteOptions> {
  /** if something typed in, get autocomplete options from backend */
  if (search.trim())
    return [
      viewAll,
      ...(await getAutocomplete(search)).items.map((item) => ({
        id: item.id,
        label: item.name || "",
        info: item.in_taxon_label || item.id,
        icon: getCategoryIcon(item.category),
        tooltip: "",
      })),
    ] satisfies AutocompleteOptions;

  /**
   * otherwise, if search box focused and nothing is typed in yet, show some
   * useful entries
   */

  /** show top N entries in each category */
  const top = 5;

  /** recent */
  const recent: AutocompleteOptions = uniqBy([...history.value].reverse(), "id")
    .slice(0, top)
    .map((entry) => ({
      ...entry,
      icon: "clock-rotate-left",
      tooltip: "Node you recently visited",
    }));

  /** popular */
  const popular: AutocompleteOptions = sortBy(
    Object.entries(groupBy(history.value, "id")).map(([, matches]) => ({
      entry: matches[0],
      count: matches.length,
    })),
    "count",
  )
    .filter(({ count }) => count >= 3)
    .reverse()
    .slice(0, top)
    .map(({ entry }) => ({
      ...entry,
      icon: "person-running",
      tooltip: "Node you frequently visit",
    }));

  /** examples */
  const examples: AutocompleteOptions = [
    { id: "MONDO:0007523", label: "Ehlers-Danlos hypermobility" },
    { id: "FB:FBgn0029157", label: "SSH" },
    { id: "MONDO:0015988", label: "Multicystic kidney dysplasia" },
  ].map((entry) => ({
    ...entry,
    icon: "lightbulb",
    tooltip: "Example node",
  }));

  return [...recent, ...popular, ...examples];
}

onMounted(async () => {
  const response = await getSearch("", 0, 0);
  facets.value = response.facet_fields || [];

  const options: Record<string, MultiOptions> = {};
  for (const facet of facets.value) {
    options[facet.label || ""] = (facet.facet_values || []).map(
      (facet_value) => ({
        id: facet_value.label,
        label: startCase(facet_value.label),
        count: facet_value.count ?? 0,
      }),
    );
  }
  dropdownsOptions.value = options;
  dropdownsSelected.value = JSON.parse(JSON.stringify(options));
});
</script>

<style lang="scss" scoped>
.title {
  display: flex;
  position: relative;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  text-align: left;
}

.title-name {
  flex-grow: 0;
}

.title-name > :deep(svg) {
  font-size: 2rem;
}

.title-taxon {
  color: $dark-gray;
  font-size: 0.9rem;
  text-align: left;
}

.title-id {
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
  color: $dark-gray;
  font-size: 0.9rem;
  text-align: left;

  span {
    width: 100%;
  }
}

.page-button {
  height: 30px;
  padding: 0 3px;
  border-radius: $rounded;
  color: $theme;
  transition: box-shadow $fast;

  &:hover {
    box-shadow: $outline;
  }
}

.header-box {
  width: 100%;
}
.header-box :deep(input) {
  border-top-width: 0;
  border-right-width: 0;
  border-left-width: 0;
  border-radius: 0;
  border-color: currentColor;
  background: none;
  color: currentColor;
}

.header-box :deep(.icon) {
  color: currentColor !important;
}

.hilite {
  font-style: normal;
  font-weight: 600;
}

.help-icon {
  margin-left: 10px;
  font-weight: bolder;
  font-size: 1.3em;
}

.help-icon-section {
  display: flex;
  align-items: center;
  width: 100%;
}

.search-input {
  flex-grow: 1;
}
</style>
