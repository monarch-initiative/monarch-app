<template>
  <AppBreadcrumb />
  <PageTitle id="phenotype-similarity" title="Phenotype Similarity Tools" />

  <AppSection width="big">
    <p class="description">
      Use powerful semantic similarity tools — based on metrics like Jaccard,
      Ancestor Information Content, and Phenodigm.
    </p>

    <div class="tabs">
      <div class="tab-item" :class="{ active: activeTab === 'search' }">
        <AppButton
          v-tooltip="
            `Find genes or diseases from a species or group based on input phenotypes.`
          "
          :class="{ active: activeTab === 'search' }"
          text="Similarity Search"
          icon="magnifying-glass"
          color="none"
          @click="setTab('search')"
        />
        <p class="tab-description">Search for related genes and diseases</p>
      </div>

      <div class="tab-item" :class="{ active: activeTab === 'compare' }">
        <AppButton
          v-tooltip="
            `Directly compare two sets of phenotypes to evaluate their similarity.`
          "
          :class="{ active: activeTab === 'compare' }"
          text="Similarity Compare"
          icon="compare-icon"
          color="none"
          @click="setTab('compare')"
        />
        <p class="tab-description">Compare two sets of phenotypes</p>
      </div>
    </div>
  </AppSection>
  <div>
    <PagePhenotypeSearch v-if="activeTab === 'search'" />
    <PagePhenotypeCompare v-else />
  </div>
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
  flex-wrap: wrap;
  width: 80%;
  background-color: #fff;

  @media (max-width: $wrap) {
    width: 90%;
  }
  :deep(.button) {
    &:hover,
    &:focus {
      outline: none !important;
      box-shadow: none !important;
    }
  }
  .tab-item.active {
    border: 1px solid #ccc;
    border-bottom: 3px solid $theme; // keep consistent height
    background-color: $theme;
    color: $white;

    .tab-description {
      color: $white;
    }

    :deep(.button) {
      background-color: transparent !important;
      color: $white !important;
    }
  }

  .tab-item:not(.active) {
    border: 1px solid transparent;
    border-bottom: 3px solid $theme;
    background-color: $light-gray;
    transition: background-color 0.3s;

    &:hover {
      background-color: #cccccc;
    }

    .tab-description {
      color: #555;
    }

    :deep(.button) {
      background-color: transparent !important;
      color: $theme;
    }
  }

  button {
    width: 100%;
    border: none !important;

    font-weight: bold;
    white-space: nowrap;
    cursor: pointer;
    transition:
      background 0.3s,
      color 0.3s;
    &.active {
      z-index: 1;
      transition:
        background 0.3s,
        color 0.3s;
    }

    &:not(.active) {
      border-bottom: 3px solid $theme;
      background-color: $light-gray;
    }
    &:not(.active):hover {
      background-color: #cccccc;
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
  padding-bottom: 0.2em;
  color: #555;
  font-size: 0.8em;
  text-align: center;
}
</style>
