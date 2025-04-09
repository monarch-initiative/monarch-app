<template>
  <AppBreadcrumb class="breadcrumb" />
  <AppSection width="big" design="bare">
    <div class="container">
      <div class="logo-container">
        <img src="/icons/monarch-logo.svg" alt="logo" class="logo" />
        <h3>Knowledge Graph</h3>
      </div>

      <div :class="['page-wrapper', { 'search-active': search }]">
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
        <SearchSuggestions @select="handleSuggestionClick" />

        <div class="tool-section">
          <p>
            In addition to the comprehensive search above you can explore the
            Monarch KG with our cutting-edge tool suite
          </p>
          <div class="tools">
            <AppLink to="/kg/compare-phenotypes" class="tool"
              >Phenotype Similarity Compare</AppLink
            >
            <AppLink to="/kg/search-phenotypes" class="tool"
              >Phenotype Similarity Search</AppLink
            >
            <AppLink
              to="https://monarch-initiative.github.io/monarchr/articles/monarchr"
              class="tool"
              >Monarch R</AppLink
            >
            <AppLink
              to="https://neo4j.monarchinitiative.org/browser/"
              class="tool"
              >Neo4j</AppLink
            >
            <AppLink to="/kg/text-annotator" class="tool"
              >Text Annotator</AppLink
            >
            <AppLink
              to="https://github.com/monarch-initiative/monarch-assistant-cypher"
              class="tool"
              >Monarch Assistant</AppLink
            >
            <AppLink
              to="https://api-v3.monarchinitiative.org/v3/docs"
              class="tool"
              >MonarchKG API</AppLink
            >
          </div>
        </div>
      </div>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { groupBy, sortBy, uniqBy } from "lodash";
import { getCategoryIcon } from "@/api/categories";
import { getAutocomplete } from "@/api/search";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSelectAutocomplete, {
  type Options as AutocompleteOptions,
  type Option,
} from "@/components/AppSelectAutocomplete.vue";
import SearchSuggestions from "@/components/TheSearchSuggestions.vue";
import { history } from "@/global/history";
import { waitFor } from "@/util/dom";

const search = ref("");
const router = useRouter();

const viewAll: Option = {
  id: "ALL",
  label: "View all results...",
  icon: "arrow-right",
  special: true,
};

const ENTITY_MAP: Record<
  string,
  { id: string; label: string; to?: string; text?: string }
> = {
  "Ehlers-Danlos syndrome": {
    id: "MONDO:0020066",
    label: "Ehlers-Danlos syndrome",
    to: "disease-to-phenotype",
  },
  "Down syndrome": {
    id: "MONDO:0008608",
    label: "Down syndrome",
    to: "disease-model",
  },
  "cystic fibrosis": {
    id: "MONDO:0009061",
    label: "Cystic fibrosis",
    to: "variant-to-disease",
  },
  FBN1: {
    id: "HGNC:3603",
    label: "FBN1",
    to: "gene-to-phenotype",
  },
};

const handleSuggestionClick = async (term: string) => {
  const entity = ENTITY_MAP[term];
  if (entity?.id) {
    await router.push({ path: "/" + entity.id, hash: "#" + entity.to });
  } else {
    await router.push({
      name: "KnowledgeGraphResults",
      query: { search: term },
      hash: "#search",
    });
  }
};

const onChange = async (value: string | Option, originalSearch: string) => {
  if (typeof value !== "string" && value.id && value.id !== viewAll.id) {
    await router.push("/" + value.id);
  } else {
    await router.push({
      name: "KnowledgeGraphResults",
      query: { search: originalSearch },
      hash: "#search",
    });
  }
};

const runGetAutocomplete = async (
  search: string,
): Promise<AutocompleteOptions> => {
  if (search.trim()) {
    const items = (await getAutocomplete(search)).items || [];
    return [
      viewAll,
      ...items.map((item) => ({
        id: item.id,
        label: item.name || "",
        info: item.in_taxon_label || item.id,
        icon: getCategoryIcon(item.category),
        tooltip: "",
      })),
    ];
  }

  const top = 5;
  const recent = uniqBy([...history.value].reverse(), "id")
    .slice(0, top)
    .map((entry) => ({
      ...entry,
      icon: "clock-rotate-left",
      tooltip: "Node you recently visited",
    }));

  const popular = sortBy(
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
};

const onFocus = async () => {
  const input = await waitFor<HTMLInputElement>("input");
  input?.focus();
};

const onDelete = () => {
  search.value = "";
};
</script>

<style scoped lang="scss">
.breadcrumb {
  margin: 0;
}

.section {
  justify-content: center;
}
.container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  overflow-x: hidden;
  gap: 3em;
  text-align: center;
}

.page-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 60em;
  overflow-x: hidden;
  transition: all 0.3s ease;
}

.search-box {
  width: 100%;
  max-width: 600px;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  .h3 {
    padding: 0;
  }
}

.logo {
  height: 2em;
}

.tool-section {
  display: flex;
  flex-direction: column;
  max-width: 40em;
  margin: 2em;
  gap: 1.2em;

  font-size: 0.9em;

  p {
    line-height: 1.5;
    text-align: center;
  }

  .tools {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.9rem;

    .tool {
      color: #007bff;
      font-weight: 500;
      text-decoration: underline;
      cursor: pointer;
    }
  }
}
</style>
