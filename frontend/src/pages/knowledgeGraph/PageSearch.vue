<template>
  <AppBreadcrumb />
  <div class="container">
    <AppSection width="big" class="section" design="bare">
      <div class="logo-container">
        <img src="/icons/monarch-logo.svg" alt="logo" class="logo" />
        <h3>{{ "Knowledge Graph" }}</h3>
      </div>
      <div :class="{ 'search-active': search }" class="page-wrapper">
        <!-- Centered Search Box -->
        <div class="search-box">
          <AppSelectAutocomplete
            :model-value="search"
            name="Search"
            placeholder="Gene, disease, phenotype, etc."
            :options="runGetAutocomplete"
            @focus="onFocus"
            @change="onChange"
            @delete="onDelete"
          />
        </div>
        <SearchSuggestions
          :suggestions="searchSuggestions"
          @select="handleSuggestionClick"
        />
        <div class="toolSection">
          <p>
            In addition to the comprehensive search above you can explore the
            Monarch KG with our cutting-edge tool suite
          </p>
          <div class="tools">
            <span class="tool">{{ "Phenotype Similarity Compare" }}</span>
            <span class="tool">{{ "Phenotype Similarity Search" }}</span>
            <span class="tool">{{ " Monarch R" }}</span>
            <span class="tool">{{ "Neo4j" }}</span>
            <span class="tool">{{ "Text Annotator" }}</span>
            <span class="tool">{{ "Monarch Assistant" }}</span>
            <span class="tool">{{ " MonarchKG API" }}</span>
          </div>
        </div>
      </div>
    </AppSection>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { groupBy, mapValues, sortBy, startCase, uniq, uniqBy } from "lodash";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import type { SearchResults } from "@/api/model";
import { getAutocomplete, getSearch } from "@/api/search";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppButton from "@/components/AppButton.vue";
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
import { appTitle } from "@/global/meta";
import { waitFor } from "@/util/dom";
import SearchSuggestions from "./PageSearchSuggestions.vue";

type Props = {
  /** whether to show pared down version with just search box */
  minimal?: boolean;
  /** whether search box is in header */
  headerBox?: boolean;
  /** whether to navigate to explore page when focusing search box */
  focusExplore?: boolean;
  /** whether this is being shown on the home page */
  home?: boolean;
};

const props = defineProps<Props>();

const search = ref("");
/** route info */
const router = useRouter();
// Removed unused variable 'route'

/** autocomplete option for viewing all/detailed results */
const viewAll: Option = {
  id: "ALL",
  label: "View all results...",
  icon: "arrow-right",
  // info: "on explore page",
  special: true,
};

const ENTITY_MAP: Record<string, { id: string; label: string; to?: string }> = {
  "Ehlers-Danlos syndrome": {
    id: "MONDO:0020066",
    label: "Ehlers-Danlos syndrome",
    to: "disease-to-phenotype",
  },
};

const searchSuggestions = [
  { label: "Disease to Gene", term: "Ehlers-Danlos syndrome" },
  { label: "Disease to Model", term: "Ehlers-Danlos syndrome" },
  {
    label: "Variant to disease/Phenotype",
    term: "Ehlers-Danlos syndrome",
  },
  { label: "Gene to Phenotype", term: "Ehlers-Danlos syndrome" },
];

const handleSuggestionClick = async (term: string) => {
  console.log("term", term);
  const entity = ENTITY_MAP[term];
  console.log("enity", entity);
  if (entity?.id) {
    await router.push({ path: "/" + entity.id, hash: "#" + entity.to });
  } else {
    console.warn("Entity not found, fallback to search");
    await router.push({
      name: "KnowledgeGraphResults",
      query: { search: term },
      hash: "#search",
    });
  }
};

/** when user "submits" search */
async function onChange(value: string | Option, originalSearch: string) {
  console.log({ value, originalSearch });
  if (typeof value !== "string" && value.id && value.id !== viewAll.id) {
    /** go directly to node page of selected option */
    await router.push("/" + value.id);
  } else {
    /** if in header and search cleared, don't navigate away */
    if (props.headerBox && !originalSearch) return;
    /** view all results on explore page */

    await router.push({
      name: "KnowledgeGraphResults",
      query: {
        search: originalSearch,
      },
      hash: "#search",
    });
  }
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

/** when user focuses text box */
async function onFocus() {
  if (!props.focusExplore) return;

  /** navigate to explore page */
  await router.push("/explore");
  /** refocus box */
  const input = await waitFor<HTMLInputElement>("input");
  input?.focus();
}

const onDelete = () => {
  search.value = "";
};
</script>

<style lang="scss" scoped>
.container {
  position: fixed;
  top: 4.5em;
  right: 0;
  bottom: 0;
  left: 0;
}
.page-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;

  transition: all 0.3s ease;
}

.search-box {
  display: flex;
  justify-content: center;
  width: 100%;
  max-width: 600px;
  transition: all 0.3s ease;
}

/* Center search box when no search term */
.page-wrapper:not(.search-active) .search-box {
  flex: 1; /* Center the search box vertically */
  align-items: center;
  margin: 0 auto;
}

/* Sticky search box after search term */
.search-active .search-box {
  z-index: 10;
  position: sticky;
  top: 0;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Results section */
.results {
  flex: 1;
  width: 100%;
  max-width: 800px;
  padding-top: 2rem;
  overflow: hidden;
}

.section.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6em;
}

.logo-container {
  display: flex;
  flex-direction: column;

  h3 {
    padding: 0.2em;
  }
}

.logo {
  height: 2em;
}

.toolSection {
  max-width: 35em;
  margin: 3em auto;
  font-size: 0.8em;
  text-align: center;

  p {
    margin-bottom: 1em;
    line-height: 1.6em;
    text-align: center;
  }

  .tools {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;

    .tool {
      flex: 1 1 auto;
      max-width: fit-content;
      padding: 0.5em;
      color: #007bff;
      text-align: center;
      text-decoration: underline;
      white-space: normal;
      cursor: pointer;
      word-wrap: break-word;
      font-weight: 500;
    }
  }
}
</style>
