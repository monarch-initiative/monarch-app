<!--
  node landing page
-->

<template>
  <!-- status -->
  <template v-if="isLoading || isError">
    <AppSection design="fill" class="section">
      <AppHeading
        class="heading"
        :icon="`category-${kebabCase(String($route.params.category))}`"
      >
        {{ $route.params.id }}
      </AppHeading>
    </AppSection>
    <AppSection>
      <AppStatus v-if="isLoading" code="loading"
        >Loading node information</AppStatus
      >
      <AppStatus v-if="isError" code="error"
        >Error loading node information</AppStatus
      >
    </AppSection>
  </template>

  <!-- results -->
  <template v-else-if="node">
    <SectionTitle :node="node" />
    <SectionOverview :node="node" />
    <SectionDetails :node="node" />
    <SectionHierarchy :node="node" />
    <SectionVisualization :node="node" />
    <!-- <SectionAssociations :node="node" /> -->
    <!-- <SectionBreadcrumbs :node="node" />  -->

    <Teleport to="body">
      <TheTableOfContents />
    </Teleport>
  </template>
</template>

<script setup lang="ts">
import { nextTick, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { kebabCase } from "lodash";
// import SectionAssociations from "./SectionAssociations.vue";
// import SectionBreadcrumbs from "./SectionBreadcrumbs.vue";
import { getEntity } from "@/api/entity";
import TheTableOfContents from "@/components/TheTableOfContents.vue";
// import { lookupNode } from "@/api/node-lookup";
import { addEntry } from "@/global/history";
import { appDescription, appTitle } from "@/global/meta";
import { scrollToHash } from "@/router";
import { useQuery } from "@/util/composables";
import SectionDetails from "./SectionDetails.vue";
import SectionHierarchy from "./SectionHierarchy.vue";
import SectionOverview from "./SectionOverview.vue";
import SectionTitle from "./SectionTitle.vue";
import SectionVisualization from "./SectionVisualization.vue";

/** route info */
const route = useRoute();

/** get new node data */
const {
  query: getNode,
  data: node,
  isLoading,
  isError,
} = useQuery(
  async function () {
    /** get node from route params */
    const { id = "" } = route.params;
    // const { id = "", category = "" } = route.params;

    /** get node information */
    const node_info = await getEntity(id as string);
    // const old_info = await lookupNode(id as string, category as string);
    // const association_counts_old = old_info.associationCounts;
    return node_info;
  },

  /** default value */
  null,

  /** on success, after data loaded */
  async (results) => {
    /** scroll to hash */
    await nextTick();
    scrollToHash();

    /**
     * set page description from node meta data. no need to include category and
     * id, as those should already be in the document title. see
     * https://metatags.io/
     */
    const { name = "", description = "" } = results || {};
    appDescription.value = [name, description]
      .filter((part) => part)
      .join(" | ");
  }
);

/** when path (not hash or query) changed, get new node data */
watch(() => route.path, getNode);

/** update document title */
watch(
  [() => route.fullPath, () => node.value?.name],
  () => {
    appTitle.value = [
      node.value?.name,
      // `${route.params.id} (${route.params.category})`,
      route.query.associations ? `${route.query.associations} assoc.` : "",
    ];
  },
  /** https://github.com/vuejs/vue-router/issues/3393 */
  { immediate: true, flush: "post" }
);

/** update node history on node visit */
watch([() => node.value?.name], () => addEntry(node.value?.name), {
  immediate: true,
});

/** get new node data on load */
onMounted(getNode);
</script>

<style lang="scss" scoped>
.heading {
  font-size: 1.2rem;
}
</style>
