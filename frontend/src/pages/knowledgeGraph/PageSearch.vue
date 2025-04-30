<template>
  <AppBreadcrumb class="breadcrumb" />
  <AppSection width="big">
    <div class="container">
      <div class="logo-container">
        <img src="/icons/monarch-logo.svg" alt="logo" class="logo" />
        <h3 id="knowledge-graph">Knowledge Graph</h3>
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
            <AppLink
              v-for="tool in TOOL_LINKS"
              :key="tool.label"
              :to="tool.to"
              :external="tool.external"
              class="tool"
            >
              {{ tool.label }}
              <AppIcon v-if="tool.external" icon="arrow-up-right-from-square" />
            </AppLink>
          </div>
        </div>
      </div>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { nextTick, ref } from "vue";
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
import { ENTITY_MAP, TOOL_LINKS } from "@/data/knowledgeGraphConfig";
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

function scrollToHashWithOffset(hash: string, offset = 80) {
  const el = document.querySelector(hash);
  if (el) {
    const y = el.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top: y, behavior: "smooth" });
  }
}

const handleSuggestionClick = async (term: string) => {
  const entity = ENTITY_MAP[term];
  if (entity?.id) {
    await router.push({ path: "/" + entity.id, hash: "#" + entity.to });

    await nextTick();
    setTimeout(() => {
      scrollToHashWithOffset(`#${entity.to}`, 80);
    }, 1000);
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
