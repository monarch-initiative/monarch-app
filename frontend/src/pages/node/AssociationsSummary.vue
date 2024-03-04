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
      <AppFlex direction="col" align-h="left" gap="small" class="info">
        <AppNodeBadge
          :node="{
            id: item.subject,
            name: item.subject_label,
            category: item.subject_category,
            info: item.subject_taxon_label,
          }"
          :breadcrumbs="getBreadcrumbs(node, item, 'subject')"
        />
        <AppPredicateBadge :association="item" :vertical="true" />
        <AppNodeBadge
          :node="{
            id: item.object,
            name: item.object_label,
            category: item.object_category,
            info: item.object_taxon_label,
          }"
          :breadcrumbs="getBreadcrumbs(node, item, 'object')"
        />
      </AppFlex>

      <AppButton
        v-tooltip="
          item.id === association?.id
            ? 'Deselect this association'
            : `Show evidence (${
                item.evidence_count || 0
              }) and other info about this association`
        "
        class="details"
        text="Details"
        :aria-pressed="item.id === association?.id"
        :icon="item.id === association?.id ? 'check' : 'flask'"
        :color="item.id === association?.id ? 'primary' : 'secondary'"
        @click="emit('select', item.id === association?.id ? undefined : item)"
      />
    </div>
  </template>
</template>

<script lang="ts">
/**
 * get breadcrumbs to add to trail when clicking on association subject or
 * object
 */
export function getBreadcrumbs(
  node: Node,
  association: DirectionalAssociation,
  side: "subject" | "object",
) {
  const subject = {
    id: association.subject,
    name: association.subject_label,
    category: association.subject_category,
    in_taxon_label: association.subject_taxon_label,
  };
  const object = {
    id: association.object,
    name: association.object_label,
    category: association.object_category,
    in_taxon_label: association.object_taxon_label,
  };

  let breadcrumbs: Breadcrumb[] | undefined = [];

  /**
   * add extra link between current node and subject/object if they are not the
   * same, e.g. current node is muscular dystrophy and association is
   * oculopharyngodistal myopathy 1 (sub-class of muscular dystrophy) -> Distal
   * muscle weakness
   */
  if (
    association.direction === AssociationDirectionEnum.outgoing
      ? subject.id !== node.id
      : object.id !== node.id
  )
    breadcrumbs.push({
      node,
      association: {
        predicate: "is super class of",
        direction: AssociationDirectionEnum.outgoing,
      },
    });

  if (
    association.direction === AssociationDirectionEnum.outgoing
      ? side === "object"
      : side === "subject"
  )
    breadcrumbs.push({
      node: side === "subject" ? object : subject,
      association,
    });

  /**
   * if we're adding two breadcrumbs, mark one has not having its own history
   * entry, so clicking on it in breadcrumbs section moves history back correct
   * number of steps
   */
  if (breadcrumbs.length === 2) breadcrumbs[1].noEntry = true;

  return breadcrumbs;
}
</script>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { getTopAssociations } from "@/api/associations";
import {
  AssociationDirectionEnum,
  type DirectionalAssociation,
  type Node,
} from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import type { Option } from "@/components/AppSelectSingle.vue";
import type { Breadcrumb } from "@/global/breadcrumbs";
import { useQuery } from "@/util/use-query";

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
      throw Error("No association info available");

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

.info {
  flex-grow: 1;
  width: 0;
  text-align: left;
}

.details {
  min-width: unset !important;
  min-height: unset !important;
}
</style>
=
