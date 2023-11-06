<!--
  node page associations section
-->

<template>
  <AppSection>
    <AppHeading icon="arrows-left-right">Associations</AppHeading>

    <span v-if="!categoryOptions.length"
      >No associations with &nbsp;<AppNodeBadge :node="node" />
    </span>

    <!-- select -->
    <AppFlex v-else gap="small">
      <span
        >Associations between &nbsp;<AppNodeBadge :node="node" />&nbsp;
        and</span
      >
      <AppSelectSingle
        v-model="category"
        name="category"
        :options="categoryOptions"
      />
    </AppFlex>

    <template v-if="category">
      <!-- table view of associations -->
      <AssociationsTable
        :node="node"
        :category="category"
        :association="association"
        @select="(value) => (association = value)"
      />
    </template>
  </AppSection>

  <!-- details viewer of association -->
  <SectionAssociationDetails
    v-if="association"
    :node="node"
    :association="association"
  />
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { startCase } from "lodash";
import type { DirectionalAssociation, Node } from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type { Option, Options } from "@/components/AppSelectSingle.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import AssociationsTable from "@/pages/node/AssociationsTable.vue";
import SectionAssociationDetails from "@/pages/node/SectionAssociationDetails.vue";

/** route info */
const route = useRoute();
const router = useRouter();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** selected category of associations to show */
const category = ref<Option>();
/** selected association id */
const association = ref<DirectionalAssociation>();

/** list of options for dropdown */
const categoryOptions = computed(
  (): Options =>
    props.node.association_counts?.map((association_count) => ({
      id: association_count.category || "",
      label: startCase(association_count.label),
      count: association_count.count,
    })) || [],
);

/** deselect association when selected category changes */
watch(category, () => (association.value = undefined));

/** update url from selected category */
watch(
  category,
  (_, oldValue) => {
    /** ignore first change to category due to auto-select */
    if (oldValue)
      router.replace({
        ...route,
        query: { associations: category.value?.id },
      });
  },
  /** avoid extra triggering of watch functions */
  { flush: "post" },
);

/** update selected category from url */
watch(
  () => route.query.associations,
  () => {
    if (!route.query.associations) return;
    category.value = categoryOptions.value.find(
      (option) => option.id === route.query.associations,
    );
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
</style>
