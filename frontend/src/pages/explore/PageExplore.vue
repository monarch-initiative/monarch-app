<!--
  explore landing page
-->

<template>
  <AppSection>
    <AppHeading>Explore</AppHeading>
         <!-- KG counts (for advertising) -->
    <AppGallery :cols="5">
      <!-- node counts -->
      <AppTile
        v-for="(item, index) in metadata.node"
        :key="index"
        :icon="item.icon"
        :title="startCase(item.label.replace(/biolink:/g, ''))"
        :subtitle="formatNumber(item.count, true)"
        design="extra-small"
      />
      <!-- association counts -->
      <AppTile
        v-for="(item, index) in metadata.association"
        :key="index"
        :icon="item.icon2 ? undefined : item.icon"
        :title="startCase(item.label.replace(/biolink:/g, ''))"
        :subtitle="formatNumber(item.count, true)"
        design="extra-small"
      >
        <AppFlex v-if="item.icon2" gap="tiny" class="association">
          <AppIcon :icon="item.icon" />
          <svg viewBox="0 0 9 2" class="line">
            <line x1="0" y1="1" x2="9" y2="1" />
          </svg>
          <AppIcon :icon="item.icon2" />
        </AppFlex>
      </AppTile>
    </AppGallery>
    <hr />
    <AppTabs v-model="tab" name="Explore Mode" :tabs="tabs" />
  </AppSection>

  <TabSearch v-if="tab === 'search'" />
  
  <TabTextAnnotator v-if="tab === 'text-annotator'" />

  <TabPhenotypeExplorer v-if="tab === 'phenotype-explorer'" />
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { startCase } from "lodash";
import AppTabs from "@/components/AppTabs.vue";
import { appTitle } from "@/global/meta";
import TabPhenotypeExplorer from "./TabPhenotypeExplorer.vue";
import tabs from "./tabs.json";
import TabSearch from "./TabSearch.vue";
import TabTextAnnotator from "./TabTextAnnotator.vue";
import { formatNumber } from "@/util/string";
import metadata from "./metadata.json";

/** route info */
const route = useRoute();

/** selected tab */
const tab = ref(tabs[0].id);

/** update document title */
watch(
  () => route.fullPath,
  () => {
    if (route.hash) appTitle.value = [startCase(route.hash)];
  },
  { immediate: true, flush: "post" },
);
</script>

<style lang="scss" scoped>
.association {
  font-size: 2rem;
}

.line {
  width: 10px;

  line {
    stroke: currentColor;
    stroke-width: 2;
    stroke-dasharray: 1 3;
    stroke-linecap: round;
  }
}
</style>

