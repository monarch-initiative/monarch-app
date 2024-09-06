<template>
  <AppSection>
    <AppGallery :cols="4">
      <!-- node counts -->
      <AppTile
        v-for="(item, index) in metadata.node"
        :key="index"
        :icon="item.icon"
        :title="startCase(item.label.replace(/biolink:/g, ''))"
        :subtitle="formatNumber(item.count, true)"
        design="small"
      />
      <!-- association counts -->
      <AppTile
        v-for="(item, index) in metadata.association"
        :key="index"
        :icon="item.icon2 ? undefined : item.icon"
        :title="startCase(item.label.replace(/biolink:/g, ''))"
        :subtitle="formatNumber(item.count, true)"
        design="small"
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
  </AppSection>
  <AppSection>
    <AppFlex gap="big">
      <AppTile
        to="https://github.com/monarch-initiative/monarchr"
        icon="diagram-project"
        title="MonarchR"
        subtitle="R package for exploring the Monarch KG locally"
      />
      <AppTile
        to="http://api-v3.monarchinitiative.org/"
        icon="code"
        title="Monarch KG API"
        subtitle="The API servingthe KG for this website"
      />
      <AppTile
        to="https://github.com/monarch-initiative/monarch-assistant-cypher"
        icon="person-running"
        title="Monarch Assistant"
        subtitle="AI Assistant for the Monarch KG"
      />
      <AppTile
        to="how-to"
        icon="circle-question"
        title="Monarch Graph Help"
        subtitle="How to use the Monarch KG"
      />
      <AppTile
        to="https://monarch-initiative.github.io/monarch-qc/"
        icon="chart-bar"
        title="Monarch Graph QC"
        subtitle="AI Assistant for the Monarch KG"
      />
    </AppFlex>
  </AppSection>
</template>
<script setup lang="ts">
import { startCase } from "lodash";
import metadata from "@/pages/explore/metadata.json";
import { formatNumber } from "@/util/string";
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
