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
      :to="`${absolute ? baseurl : '/'}${node.id}`"
      :state="
        breadcrumbs
          ? { breadcrumbs: [...currentBreadcrumbs, ...breadcrumbs] }
          : state || undefined
      "
    >
      <AppNodeText :text="name" :highlight="highlight" />
      <span v-if="infoParts.length" class="info"
        >(<template v-for="(part, index) in infoParts" :key="index"
          ><span v-if="index > 0"> | </span
          ><span :class="{ italic: part.italic }">{{
            part.text
          }}</span></template
        >)</span
      >
    </AppLink>
    <span v-else>
      <span class="name">
        <AppNodeText :text="name" :highlight="highlight" />
      </span>
      <span v-if="infoParts.length" class="info"
        >(<template v-for="(part, index) in infoParts" :key="index"
          ><span v-if="index > 0"> | </span
          ><span :class="{ italic: part.italic }">{{
            part.text
          }}</span></template
        >)</span
      >
    </span>
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import type { Node } from "@/api/model";
import AppNodeText from "@/components/AppNodeText.vue";
import { breadcrumbs as currentBreadcrumbs } from "@/global/breadcrumbs";
import type { Breadcrumb } from "@/global/breadcrumbs";

const route = useRoute();

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
  /** whether to show the node's taxon. shown by default. */
  showTaxon?: boolean;
  /** boolen to use for highlighting */
  highlight?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  icon: true,
  link: true,
  breadcrumbs: undefined,
  state: undefined,
  absolute: false,
  showId: false,
  showTaxon: true,
  highlight: false,
});

/** name/label */
const name = computed(
  () => props.node.name || props.node.label || props.node.id,
);

/**
 * Extra info shown in parens after the name, as parts rather than one joined
 * string: the taxon is a scientific name and renders italic, while the id and
 * anything else stay roman. Callers that show the taxon elsewhere (the search
 * results rows) can drop it here with :show-taxon="false".
 */
const infoParts = computed(() =>
  [
    {
      text: props.showId && name.value !== props.node.id ? props.node.id : "",
      italic: false,
    },
    {
      text: props.showTaxon ? props.node.in_taxon_label : "",
      italic: true,
    },
    { text: props.node.info, italic: false },
  ].filter((part) => !!part.text),
);

/** whether to make a link or plain text */
const isLink = computed(() => {
  const decodedPath = decodeURIComponent(route.path);
  /** make sure we're not already on the page we'd link to */
  return (
    !decodedPath.endsWith("/" + (props.node.id || "")) &&
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

/* vue condenses the whitespace between the name and this, so space it here */
.info {
  margin-left: 0.35em;
}

.italic {
  font-style: italic;
}
</style>
