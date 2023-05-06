<!--
  node page associations section, summary mode. top few associations.
-->

<template>
  <!-- status -->
  <AppStatus v-if="isLoading" code="loading"
    >Loading association summary data</AppStatus
  >
  <AppStatus v-else-if="isError" code="error"
    >Error loading association summary data</AppStatus
  >

  <!-- results -->
  <template v-else>
    <span>Top {{ associations.length }} association(s)</span>

    <!-- result -->
    <div
      v-for="(association, index) in associations"
      :key="index"
      class="result"
    >
      <AppFlex direction="col" h-align="left" gap="small" class="details">
        <!-- primary result info -->
        <div class="title">
          <AppNodeBadge :node="node" :link="false" />&nbsp;
          <AppRelationBadge :relation="association.relation" />&nbsp;
          <AppNodeBadge
            :node="association.object"
            :breadcrumb="{ node, relation: association.relation }"
          />
        </div>

        <!-- secondary result info -->
        <div class="secondary">
          <span
            >{{ association.supportCount }} piece(s) of supporting
            evidence</span
          >
        </div>
      </AppFlex>

      <AppButton
        v-tooltip="
          association.id === selectedAssociation?.id
            ? 'Viewing supporting evidence. Click again to hide.'
            : 'View supporting evidence for this association'
        "
        class="evidence"
        text="Evidence"
        :aria-pressed="association.id === selectedAssociation?.id"
        :icon="association.id === selectedAssociation?.id ? 'check' : 'flask'"
        :color="
          association.id === selectedAssociation?.id ? 'primary' : 'secondary'
        "
        @click="
          emit(
            'select',
            association.id === selectedAssociation?.id ? undefined : association
          )
        "
      />
    </div>
  </template>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import type { Association, Node } from "@/api/model";
import { getTopAssociations } from "@/api/node-associations";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppRelationBadge from "@/components/AppRelationBadge.vue";
import { useQuery } from "@/util/composables";

type Props = {
  /** current node */
  node: Node;
  /** selected association category */
  selectedCategory: string;
  /** selected association id */
  selectedAssociation?: Association;
};

const props = defineProps<Props>();

type Emits = {
  /** change selected association */
  (event: "select", value?: Association): void;
};

const emit = defineEmits<Emits>();

/** get summary association data */
const {
  query: getAssociations,
  data: associations,
  isLoading,
  isError,
} = useQuery(
  async function () {
    /** catch case where no association categories available */
    if (!props.node.association_counts?.length)
      throw new Error("No association info available");

    /** get association data */
    return await getTopAssociations(
      props.node.id,
      props.node.category,
      props.selectedCategory
    );
  },

  /** default value */
  []
);

/** get associations when category changes */
watch(() => props.selectedCategory, getAssociations);

/** get associations on load */
onMounted(getAssociations);
</script>

<style lang="scss" scoped>
.result {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 40px;
}

@media (max-width: 600px) {
  .result {
    flex-direction: column;
  }
}

.arrow {
  color: $gray;
}

.details {
  width: 0;
  flex-grow: 1;
  text-align: left;
}

.secondary {
  color: $gray;
}

.evidence {
  min-width: unset !important;
  min-height: unset !important;
}
</style>
