<!--
  node page associations section
-->

<template>
  <AppSection>
    <AppHeading icon="arrows-left-right">Associations</AppHeading>

    <!-- select -->
    <AppFlex gap="small">
      <span
        >Associations between &nbsp;<AppNodeBadge
          :node="node"
          :link="false"
        />&nbsp; and</span
      >
      <AppSelectSingle
        v-model="category"
        name="category"
        :options="categoryOptions"
      />
    </AppFlex>

    <template v-if="category">
      <!-- mode tab -->
      <AppTabs
        v-model="tab"
        :tabs="tabs"
        name="Association viewing mode"
        :url="false"
        @update:model-value="association = undefined" />

      <!-- summary view of associations -->
      <template v-if="tab === 'summary'">
        <AssociationsSummary
          :node="node"
          :selected-category="category.id"
          :selected-association="association"
          @select="(value) => (association = value)"
        />
      </template>

      <!-- table view of associations -->
      <template v-if="tab === 'table'">
        <AssociationsTable
          :node="node"
          :selected-category="category.id"
          :selected-association="association"
          @select="(value) => (association = value)"
        /> </template
    ></template>
  </AppSection>

  <!-- evidence viewer of association -->
  <EvidenceViewer
    v-if="association"
    :node="node"
    :selected-association="association"
  />
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectSingle.vue";
import AppTabs from "@/components/AppTabs.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type { Node } from "@/api/node-lookup";
import { getAssociationLabel } from "@/api/categories";
import type { Association } from "@/api/node-associations";
import AssociationsSummary from "./AssociationsSummary.vue";
import AssociationsTable from "./AssociationsTable.vue";
import EvidenceViewer from "./EvidenceViewer.vue";

/** Route info */
const router = useRouter();
const route = useRoute();

type Props = {
  /** Current node */
  node: Node;
};

const props = defineProps<Props>();

/** Mode tabs */
const tabs = [
  {
    id: "summary",
    text: "Summary",
    icon: "clipboard",
    tooltip: "Top few associations and high level details",
  },
  {
    id: "table",
    text: "Table",
    icon: "table",
    tooltip: "All association data, in tabular form",
  },
];
const tab = ref(tabs[0].id);

/** Selected category of associations to show */
const category = ref<Option>();
/** Selected association id */
const association = ref<Association>();

/** List of options for dropdown */
const categoryOptions = computed(
  (): Options =>
    props.node.associationCounts.map((association) => ({
      id: association.id,
      name: getAssociationLabel(association.id),
      icon: `category-${association.id}`,
      count: association.count,
    }))
);

/** Deselect association when selected category changes */
watch(category, () => (association.value = undefined));

/** Update url from selected category */
watch(
  category,
  () => {
    router.replace({
      ...route,
      query: { associations: category.value?.id },
    });
  },
  /** Avoid extra triggering of watch functions */
  { flush: "post" }
);

/** Update selected category from url */
watch(
  () => route.query.associations,
  () => {
    if (route.query.associations)
      category.value = categoryOptions.value.find(
        (option) => option.id === route.query.associations
      );
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
</style>
