<template>
  <AppBreadcrumb />
  <PageTitle id="phenotype-similarity" title="Phenotype Similarity Tools" />

  <AppSection width="big">
    <div class="header">
      <p class="description">
        Use powerful semantic similarity tools—based on metrics like Jaccard,
        Ancestor Information Content, and Phenodigm—to
        <strong>search</strong> for related genes and diseases, or directly
        <strong>compare</strong> two sets of phenotypes to reveal deeper
        biological insights.
      </p>
    </div>

    <div class="tabs">
      <AppButton
        :class="{ active: activeTab === 'search' }"
        @click="setTab('search')"
        text=" Similarity Search"
        icon="magnifying-glass"
        v-tooltip="
          `Find genes or diseases from a species or
            group based on input phenotypes.`
        "
        color="none"
      />

      <AppButton
        :class="{ active: activeTab === 'compare' }"
        @click="setTab('compare')"
        text="Similarity Compare"
        icon="compare-icon"
        color="none"
        v-tooltip="
          `Directly compare two sets of phenotypes to
            evaluate their similarity.`
        "
      />
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
.page {
  width: 100%;
}

.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2em;
  text-align: center;

  .title {
    font-weight: bold;
    font-size: 2rem;
  }
}

.tabs {
  display: flex;
  width: 80%;
  overflow: hidden;
  border-radius: 12px 12px 0 0;
  background: #f3f3f3;

  :deep(.button) {
    &:hover,
    &:focus {
      outline: none !important;
      box-shadow: none !important;
    }
  }

  button {
    flex: 1;
    width: 30%;
    padding: 0.75rem;
    border: none;
    background: transparent;
    color: #555;
    font-weight: 600;
    font-size: 1rem;
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

    :deep(.app-icon) {
      width: 1.2rem;
      height: 1.5rem;
      font-size: 2rem;
    }

    :deep(svg) {
      width: 1.5rem;
      height: 1.5rem;
    }
  }
}

.tagline {
  position: relative;
  max-width: 800px;
  margin: 1rem auto 0 auto;
  padding: 0 1rem;

  font-weight: 500;
  font-size: 1.1rem;
  text-align: center;

  @media (max-width: $wrap) {
    margin: 0;
  }
}
</style>
