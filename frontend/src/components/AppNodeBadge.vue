<!--
  an icon, text, and link for a node in the knowledge graph
-->

<template>
  <span class="node">
    <AppIcon
      v-if="icon"
      v-tooltip="getCategoryLabel(node.category)"
      class="icon"
      :icon="getCategoryIcon(node.category)"
    />
    <AppLink
      v-if="!currentPage"
      :to="`/node/${node.id}`"
      :state="
        breadcrumb ? { breadcrumbs: [...breadcrumbs, breadcrumb] } : undefined
      "
      >{{ node.name || node.id }}</AppLink
    >
    <span v-else class="name">{{ node.name }}</span>
    <span v-if="node.in_taxon_label"> ({{ node.info }})</span>
    <span v-if="node.info"> ({{ node.info }})</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import type { Node } from "@/api/model";
import { breadcrumbs } from "@/global/breadcrumbs";
import type { Breadcrumb } from "@/global/breadcrumbs";

type Props = {
  /** node represented by badge */
  node: Partial<Node> & {
    /** extra info to show in parens */
    info?: string;
  };
  /** whether to include icon */
  icon?: boolean;
  /**
   * breadcrumb object to add list when badge clicked on. include node that user
   * came from and relation between that node and this node.
   */
  breadcrumb?: Breadcrumb;
};

const props = withDefaults(defineProps<Props>(), {
  icon: true,
  link: true,
  breadcrumb: undefined,
});

/** whether we're already on page we're linking to */
const currentPage = computed(() =>
  window.location.pathname.endsWith("/node/" + (props.node.id || "")),
);
</script>

<style lang="scss" scoped>
.node {
  white-space: nowrap;

  & > * {
    white-space: normal;
    overflow-wrap: anywhere;
  }
}

.icon {
  position: relative;
  top: -1px;
  margin-right: 0.4em;
  vertical-align: middle;
}

.name {
  font-weight: 500;
}
</style>
