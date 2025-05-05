<template>
  <AppBreadcrumb />
  <PageTitle id="phenotype-similarity" title="Phenotype Similarity Tools" />

  <AppSection width="big">
    <p class="description">
      Use powerful semantic similarity tools — based on metrics like Jaccard,
      Ancestor Information Content, and Phenodigm.
    </p>

    <div class="tabs">
      <div class="tab-item">
        <AppButton
          :class="{ active: activeTab === 'search' }"
          @click="setTab('search')"
          text="Similarity Search"
          icon="magnifying-glass"
          v-tooltip="
            `Find genes or diseases from a species or group based on input phenotypes.`
          "
          color="none"
        />
        <p class="tab-description">Search for related genes and diseases</p>
      </div>

      <div class="tab-item">
        <AppButton
          :class="{ active: activeTab === 'compare' }"
          @click="setTab('compare')"
          text="Similarity Compare"
          icon="compare-icon"
          color="none"
          v-tooltip="
            `Directly compare two sets of phenotypes to evaluate their similarity.`
          "
        />
        <p class="tab-description">Compare two sets of phenotypes</p>
      </div>
    </div>

    <div>
      <PagePhenotypeSearch v-if="activeTab === 'search'" />
      <PagePhenotypeCompare v-else />
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import PagePhenotypeCompare from "./PagePhenotypeCompare.vue";
import PagePhenotypeSearch from "./PagePhenotypeSearch.vue";

const activeTab = ref<"search" | "compare">("search");

function setTab(tab: "search" | "compare") {
  activeTab.value = tab;
}
</script>

<style scoped lang="scss">
$wrap: 1000px;

.tabs {
  display: flex;
  width: 80%;
  overflow: hidden;
  border-radius: 12px 12px 0 0;

  :deep(.button) {
    &:hover,
    &:focus {
      outline: none !important;
      box-shadow: none !important;
    }
  }

  button {
    width: 100%;
    background-color: $light-gray;
    white-space: nowrap;
    cursor: pointer;
    transition:
      background 0.3s,
      color 0.3s;
    &.active {
      background: $theme-light;
    }
    :hover {
      box-shadow: unset;
    }

    &:not(.active):hover {
      background: #e7e7e7;
    }

    :deep(.app-icon),
    :deep(svg) {
      display: inline-block;
      width: 1.5rem !important;
      height: 1.5rem !important;
      vertical-align: middle;
    }
  }
}

.tab-item {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: stretch;
  align-items: center;
  text-align: center;
}

.tab-description {
  padding: 0.5em;
  color: #555;
  text-align: center;
}
</style>
