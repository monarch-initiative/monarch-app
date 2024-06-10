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
      v-if="isLink"
      :to="`${absolute ? baseurl : ''}${node.id}`"
      :state="
        breadcrumbs
          ? { breadcrumbs: [...currentBreadcrumbs, ...breadcrumbs] }
          : state || undefined
      "
      v-html="name"
    ></AppLink>
    <span v-else>
      <span class="name" v-html="name"></span>
      <span v-if="info">({{ info }})</span>
    </span>
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import type { Node } from "@/api/model";
import { breadcrumbs as currentBreadcrumbs } from "@/global/breadcrumbs";
import type { Breadcrumb } from "@/global/breadcrumbs";

const { VITE_URL: baseurl } = import.meta.env;

type Props = {
  /** node represented by badge */
  node: Partial<Node> & {
    /** alternative name */
    label?: string;
    /** extra info to show in parens */
    info?: string;
  };
  /** whether to include icon */
  icon?: boolean;
  /**
   * breadcrumb objects to add list when badge clicked on. include node that
   * user came from and relation between that node and this node.
   */
  breadcrumbs?: Breadcrumb[];
  /** state data to pass through to link component */
  state?: { [key: string]: unknown };
  /** whether to use absolute link */
  absolute?: boolean;
  /** whether to show id. not shown by default, unless name/label empty. */
  showId?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  icon: true,
  link: true,
  breadcrumbs: undefined,
  state: undefined,
  absolute: false,
  showId: false,
});

/** name/label */
const name = computed(
  () => props.node.name || props.node.label || props.node.id,
);

/** extra info */
const info = computed(() =>
  [
    props.showId && name.value !== props.node.id ? props.node.id : "",
    props.node.in_taxon_label,
    props.node.info,
  ]
    .filter(Boolean)
    .join(" | "),
);

/** whether to make a link or plain text */
const isLink = computed(() => {
  /** make sure we're already on page we're linking to */
  return (
    !window.location.pathname.endsWith("/node/" + (props.node.id || "")) &&
    /** make sure id is a valid curie */
    !!props.node.id?.match(/^\w/)
  );
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
