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
    <span>Top {{ associations.items.length }} association(s)</span>

    <!-- result -->
    <div
      v-for="(item, index) in associations.items"
      :key="index"
      class="result"
    >
      <AppFlex direction="col" align-h="left" gap="small" class="details">
        <AppNodeBadge
          :node="{
            id: item.subject,
            name: item.subject_label,
            category: item.subject_category,
          }"
          :link="node.id === item.object"
        />
        <AppPredicateBadge :association="item" :vertical="true" />
        <AppNodeBadge
          :node="{
            id: item.object,
            name: item.object_label,
            category: item.object_category,
          }"
          :link="node.id === item.subject"
        />
      </AppFlex>

      <AppButton
        v-tooltip="
          item.id === association?.id
            ? 'Viewing supporting evidence. Click again to hide.'
            : 'View supporting evidence for this association'
        "
        class="evidence"
        :text="`Evidence (${item?.evidence_count || 0})`"
        :aria-pressed="item.id === association?.id"
        :icon="item.id === association?.id ? 'check' : 'flask'"
        :color="item.id === association?.id ? 'primary' : 'secondary'"
        @click="emit('select', item.id === association?.id ? undefined : item)"
      />
    </div>
  </template>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { getTopAssociations } from "@/api/associations";
import type { DirectionalAssociation, Node } from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import type { Option } from "@/components/AppSelectSingle.vue";
import { useQuery } from "@/util/composables";

type Props = {
  /** current node */
  node: Node;
  /** selected association category */
  category: Option;
  /** selected association */
  association?: DirectionalAssociation;
};

const props = defineProps<Props>();

type Emits = {
  /** change selected association */
  select: [value?: DirectionalAssociation];
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
    if (!props.node.association_counts.length)
      throw new Error("No association info available");

    /** get association data */
    return await getTopAssociations(props.node.id, props.category.id);
  },

  /** default value */
  { items: [], limit: 0, offset: 0, total: 0 },
);

/** get associations when category changes */
watch(() => props.category, getAssociations);

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
  flex-grow: 1;
  width: 0;
  text-align: left;
}

.evidence {
  min-width: unset !important;
  min-height: unset !important;
}
</style>
=
