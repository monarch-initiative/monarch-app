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
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getAssociationLabel } from "@/api/categories";
import type { Association } from "@/api/node-associations";
import type { Node } from "@/api/node-lookup";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type { Option, Options } from "@/components/AppSelectSingle.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import AppTabs from "@/components/AppTabs.vue";
import AssociationsSummary from "./AssociationsSummary.vue";
import AssociationsTable from "./AssociationsTable.vue";
import EvidenceViewer from "./EvidenceViewer.vue";

/** route info */
const router = useRouter();
const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** mode tabs */
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

/** selected category of associations to show */
const category = ref<Option>();
/** selected association id */
const association = ref<Association>();

/** list of options for dropdown */
const categoryOptions = computed(
  (): Options =>
    props.node.associationCounts.map((association) => ({
      id: association.id,
      name: getAssociationLabel(association.id),
      icon: `category-${association.id}`,
      count: association.count,
    }))
);

/** deselect association when selected category changes */
watch(category, () => (association.value = undefined));

/** update url from selected category */
watch(
  category,
  () => {
    router.replace({
      ...route,
      query: { associations: category.value?.id },
    });
  },
  /** avoid extra triggering of watch functions */
  { flush: "post" }
);

/** update selected category from url */
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
