<!--
  node landing page
-->

<template>
  <!-- status -->
  <template v-if="isLoading || isError">
    <AppSection width="full" design="fill" class="node">
      <AppHeading class="heading">
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
    <SectionVisualization :node="node" />
    <SectionAssociations :node="node" />
    <SectionBreadcrumbs :node="node" />
    <SectionHierarchy :node="node" />
    <Teleport to="body">
      <TheTableOfContents />
    </Teleport>
  </template>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { getNode } from "@/api/node";
import TheTableOfContents from "@/components/TheTableOfContents.vue";
import { useQuery } from "@/composables/use-query";
import { addEntry } from "@/global/history";
import { appDescription, appTitle } from "@/global/meta";
import SectionBreadcrumbs from "@/pages/node/SectionBreadcrumbs.vue";
import SectionAssociations from "./SectionAssociations.vue";
import SectionHierarchy from "./SectionHierarchy.vue";
import SectionOverview from "./SectionOverview.vue";
import SectionTitle from "./SectionTitle.vue";
import SectionVisualization from "./SectionVisualization.vue";

/** route info */
const route = useRoute();

/** get new node data */
const {
  query: runGetNode,
  data: node,
  isLoading,
  isError,
} = useQuery(
  async function () {
    /** get node from route params */
    const { id = "" } = route.params;

    if (!id) return null;
    const node_info = await getNode(String(id));

    return node_info;
  },

  /** default value */
  null,

  /** on success, after data loaded */
  async (results) => {
    /**
     * set page description from node metadata. no need to include category and
     * id, as those should already be in the document title. see
     * https://metatags.io/
     */
    const { name = "", description = "" } = results || {};
    appDescription.value = [name, description]
      .filter((part) => part)
      .join(" | ");
  },
);

/** when path (not hash or query) changed, get new node data */
watch(() => route.path, runGetNode);

/** update document title */
watch(
  [() => route.fullPath, () => node.value?.name],
  () => {
    appTitle.value = [
      node.value?.name || String(route.params.id),
      // `${route.params.id} (${route.params.category})`,
      route.query.associations ? `${route.query.associations} assoc.` : "",
    ];
  },
  /** https://github.com/vuejs/vue-router/issues/3393 */
  { immediate: true, flush: "post" },
);

/** update node history on node visit */
watch(
  [() => node.value?.name],
  () => {
    if (node.value)
      addEntry({
        id: node.value.id,
        label: node.value.name || "",
      });
  },
  {
    immediate: true,
  },
);

/** get new node data on load */
onMounted(runGetNode);
</script>

<style lang="scss" scoped>
.heading {
  font-size: 1.2rem;
}

/** make room for the table of contents **/
.section {
  margin: 10px 20px 10px $toc-width + 20px;
  @media (max-width: 1240px) {
    margin: 10px 20px 10px 20px;
  }
}
</style>
