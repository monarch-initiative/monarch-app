<!--
  node page associations section
-->

<template>
  <!-- show an AppSection for each category in categoryOptions  -->
  <div v-for="category in categoryOptions" :key="category.id">
    <!-- Association table -->
    <AppSection alignment="left" width="full" class="inset">
      <AppHeading :level="3">{{ category.label }}</AppHeading>
      <span v-if="!categoryOptions.length"
        >No associations with &nbsp;<AppNodeBadge :node="node" />
      </span>

      <AppFlex gap="small">
        <AppCheckbox
          v-if="
            node.category === 'biolink:Gene' &&
            category?.id.startsWith('biolink:GeneToPheno')
          "
          v-model="includeOrthologs"
          v-tooltip="
            'Include phenotypes for orthologous genes in the associations table'
          "
          text="Include ortholog phenotypes"
        />
        <AppButton
          v-if="
            (node.category === 'biolink:Disease' &&
              category?.id.startsWith('biolink:DiseaseToPheno')) ||
            (node.category === 'biolink:Gene' &&
              category?.id.startsWith('biolink:GeneToPheno'))
          "
          v-tooltip="
            'Send these phenotypes to Phenotype Explorer for comparison'
          "
          to="explore#phenotype-explorer"
          :state="{ search: node.id }"
          text="Phenotype Explorer"
          icon="arrow-right"
        />
      </AppFlex>

      <template v-if="category && direct">
        <!-- table view of associations -->
        <AssociationsTable
          :node="node"
          :category="category"
          :include-orthologs="includeOrthologs"
          :direct="direct"
        />
      </template>
    </AppSection>
    <!-- details viewer of association -->
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { startCase } from "lodash";
import type { Node } from "@/api/model";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type { Option, Options } from "@/components/AppSelectSingle.vue";
import AssociationsTable from "@/pages/node/AssociationsTable.vue";

/** route info */
const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** include orthologous genes in association table */
const includeOrthologs = ref(false);
const direct = ref<Option>();

/** list of options for dropdown */
const categoryOptions = computed(
  (): Options =>
    props.node.association_counts?.map((association_count) => ({
      id: association_count.category || "",
      label: startCase(association_count.label),
      count: association_count.count,
    })) || [],
);

const directOptions = computed(
  (): Options => [
    { id: "false", label: "including sub-classes" },
    { id: "true", label: "directly" },
  ],
);

watch(
  () => route.query,
  () => {
    if (!route.query.direct) {
      direct.value = directOptions.value.find(
        (option) => option.id === "false",
      ); // Set default value
    } else {
      direct.value = directOptions.value.find(
        (option) => option.id === route.query.direct,
      );
    }
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
/** make room for the table of contents **/
.section {
  margin: 10px 20px 10px $toc-width + 20px !important;
}
</style>
