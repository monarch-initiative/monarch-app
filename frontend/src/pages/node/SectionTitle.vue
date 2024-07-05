<!--
  node page title section, at top, below header. basic identifying info of node.
-->

<template>
  <AppSection design="fill" class="section">
    <AppFlex dir="column">
      <AppHeading class="heading" :icon="getCategoryIcon(node.category)">
        <span
          :style="{ textDecoration: node.deprecated ? 'line-through' : '' }"
          v-html="node.name"
        >
        </span>
        <template v-if="node.deprecated"> (OBSOLETE)</template>
      </AppHeading>

      <AppFlex>
        <span>
          {{ getCategoryLabel(node.category) }}
        </span>
        <AppButton
          v-tooltip="'ID of this node (click to copy)'"
          design="small"
          color="secondary"
          icon="barcode"
          :text="node.id"
          :copy="true"
        />
      </AppFlex>

      <AppButton
        v-if="fromSearch"
        icon="arrow-left"
        :text="`Back to search &quot;${fromSearch}&quot;`"
        design="small"
        @click="$router.go(-1)"
      />
    </AppFlex>
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { truncate } from "lodash";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import type { Node } from "@/api/model";
import { parse } from "@/util/object";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();

/** checking if coming from search */
const fromSearch = computed(() =>
  truncate(parse(window.history.state.fromSearch, "")),
);
</script>

<style lang="scss" scoped>
.section {
  padding-top: 30px !important;
  padding-bottom: 30px !important;
}

.heading {
  padding: 0;
  font-size: 1.2rem;
}

.original-id {
  color: $dark-gray;
  font-style: italic;
  font-size: 0.9rem;
}
</style>
