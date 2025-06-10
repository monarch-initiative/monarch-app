<!--
  node page title section, at top, below header. basic identifying info of node.
-->

<template>
  <AppSection width="full" alignment="left" class="section">
    <AppFlex direction="col">
      <AppFlex align-h="right">
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

      <AppHeading
        class="heading"
        :level="1"
        :icon="getCategoryIcon(node.category)"
      >
        <span
          :style="{ textDecoration: node.deprecated ? 'line-through' : '' }"
        >
          <AppNodeText :text="node.name" />
        </span>
        <p v-if="node.id?.includes('MONDO')" class="tag">
          {{ node.id }}
        </p>
        <template v-if="node.deprecated"> (OBSOLETE)</template>
      </AppHeading>

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
import AppNodeText from "@/components/AppNodeText.vue";
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
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 0;
  gap: 0.5em;
  font-size: 1.2rem;
}

.original-id {
  color: $dark-gray;
  font-style: italic;
  font-size: 0.9rem;
}

.tag {
  padding: 4px 10px;
  border-radius: 8px;
  background-color: #eef6f9;
  color: $theme;
  font-weight: 600;
  font-size: 0.85rem;
  font-family: monospace;
  letter-spacing: 0.5px;
}
</style>
