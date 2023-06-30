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
      v-if="link"
      :to="`/node/${node.id}`"
      :state="
        breadcrumb ? { breadcrumbs: [...breadcrumbs, breadcrumb] } : undefined
      "
      >{{ node.name || node.id }}</AppLink
    >
    <span v-else class="name">{{ node.name }}</span>
  </span>
</template>

<script setup lang="ts">
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import type { Node } from "@/api/model";
import { breadcrumbs } from "@/global/breadcrumbs";

type Props = {
  /** node represented by badge */
  node: Pick<Node, "id" | "name" | "category">;
  /** whether to include icon */
  icon?: boolean;
  /** whether to include link */
  link?: boolean;
  /**
   * breadcrumb object to add list when badge clicked on. include node that user
   * came from and relation between that node and this node.
   */
  breadcrumb?: { [key: string]: unknown };
};

withDefaults(defineProps<Props>(), {
  icon: true,
  link: true,
  breadcrumb: undefined,
});
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
