<template>
  <AppSection v-if="breadcrumbs.length">
    <AppHeading icon="location-dot">Breadcrumbs</AppHeading>

    <span
      >How you got to <AppNodeBadge :node="node" /> through the Monarch
      knowledge graph:</span
    >

    <AppFlex direction="col">
      <template v-for="(breadcrumb, index) of breadcrumbs" :key="index">
        <!-- node -->
        <AppNodeBadge
          :node="breadcrumb.node"
          @click.prevent.capture="$router.go(-breadcrumbs.length + index)"
        />
        <!-- predicate -->
        <AppPredicateBadge
          :association="breadcrumb.association"
          :vertical="true"
          :reverse="
            breadcrumb.association.direction ===
            AssociationDirectionEnum.incoming
          "
        />
      </template>

      <!-- ending/current node -->
      <AppNodeBadge :node="node" />
    </AppFlex>

    <!-- clear button -->
    <AppButton
      v-tooltip="'Clear breadcrumb history'"
      icon="times"
      text="Clear"
      design="small"
      @click="clear"
    />
  </AppSection>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useRoute } from "vue-router";
import { AssociationDirectionEnum, type Node } from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import { breadcrumbs, updateBreadcrumbs } from "@/global/breadcrumbs";

interface Props {
  /** current node */
  node: Node;
}

defineProps<Props>();

/** route info */
const route = useRoute();

/** keep breadcrumbs global variable in sync with history.state.breadcrumbs */
watch(() => route, updateBreadcrumbs, { immediate: true, deep: true });

/** clear breadcrumbs history */
function clear() {
  /**
   * confirmation warning not necessary since back button should return to
   * previous state
   */
  window.history.pushState({}, "");
  updateBreadcrumbs();
}
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
</style>
