<template>
  <AppBreadcrumb />
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
      <div class="suggestions">
        <div class="tooltip-wrapper">
          <span class="tooltip-trigger">Disease to Gene</span>
          <div class="tooltip-box">
            e.g: Explore the disease to phenotype relation for
            <span
              class="tooltip-suggestion"
              @click="handleSuggestionClick('Ehlers-Danlos syndrome')"
            >
              Ehlers-Danlos Syndrome
            </span>
          </div>
        </div>
        <div class="tooltip-wrapper">
          <span class="tooltip-trigger">Disease to Model</span>
          <div class="tooltip-box">
            e.g: Explore the disease to phenotype relation for
            <span
              class="tooltip-suggestion"
              @click="handleSuggestionClick('Ehlers-Danlos syndrome')"
            >
              Ehlers-Danlos Syndrome
            </span>
          </div>
        </div>
        <div class="tooltip-wrapper">
          <span class="tooltip-trigger">Variant to disease/Phenotype</span>
          <div class="tooltip-box">
            e.g: Explore the disease to phenotype relation for
            <span
              class="tooltip-suggestion"
              @click="handleSuggestionClick('Ehlers-Danlos syndrome')"
            >
              Ehlers-Danlos Syndrome
            </span>
          </div>
        </div>

        <div class="tooltip-wrapper">
          <span class="tooltip-trigger">Gene to Phenotype</span>
          <div class="tooltip-box">
            e.g: Explore the disease to phenotype relation for
            <span
              class="tooltip-suggestion"
              @click="handleSuggestionClick('Ehlers-Danlos syndrome')"
            >
              Ehlers-Danlos Syndrome
            </span>
          </div>
        </div>
      </div>
    </div>
  </AppSection>
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
const route = useRoute();

/** autocomplete option for viewing all/detailed results */
const viewAll: Option = {
  id: "ALL",
  label: "View all results...",
  icon: "arrow-right",
  // info: "on explore page",
  special: true,
};

const ENTITY_MAP: Record<string, { id: string; label: string }> = {
  "Ehlers-Danlos syndrome": {
    id: "MONDO:0020066",
    label: "Ehlers-Danlos syndrome",
  },
};

const setSearch = (value: string) => {
  search.value = value;
};

const handleSuggestionClick = async (term: string) => {
  console.log("term", term);
  const entity = ENTITY_MAP[term];
  console.log("enity", entity);
  if (entity?.id) {
    await router.push("/" + entity.id);
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

  console.log("RUN AUTOCOMPLETE", search);
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

<style scoped>
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

.tooltip-wrapper {
  display: inline-flex;
  position: relative;
  flex-direction: column;
  align-items: center;
}

.tooltip-trigger {
  color: #007bff;
  font-size: 0.9rem;
  text-decoration: underline;
  cursor: pointer;
}

/* Tooltip box positioned directly under the trigger */
.tooltip-box {
  z-index: 999;
  position: absolute;
  top: 100%; /* position below the trigger */
  left: 50%; /* this is crucial! */
  width: 40em;
  margin-top: 1px;
  padding: 8px 12px;
  transform: translateX(-50%); /* center it */

  border-radius: 6px;
  background-color: #e8e2e2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: #000;
  font-size: 0.8rem;
  line-height: 1.4;
  white-space: normal;
  word-wrap: break-word;

  visibility: hidden;
  opacity: 0;
  pointer-events: auto;
  transition: opacity 0.2s ease;
}

/* Keep tooltip open if hovering on wrapper OR box */
.tooltip-wrapper:hover .tooltip-box {
  visibility: visible;
  opacity: 1;
}

/* Tooltip arrow */
.tooltip-box::after {
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent #e8e2e2 transparent;
  content: "";
}

/* Suggestion styling */
.tooltip-suggestion {
  margin-left: 4px;
  color: hsl(185, 100%, 30%);
  text-decoration: underline;
  cursor: pointer;
}

.tooltip-suggestion:hover {
  color: #0056b3;
}

.suggestions {
  display: flex;
  margin: 1em;
  gap: 1em;
}
</style>
