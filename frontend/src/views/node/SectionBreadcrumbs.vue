<template>
  <AppSection v-if="breadcrumbs.length">
    <AppHeading icon="location-dot">Breadcrumbs</AppHeading>

    <div>
      How you got to &nbsp;<AppNodeBadge :node="node" :link="false" />&nbsp;
      through the knowledge graph
    </div>

    <AppFlex direction="col" gap="small">
      <template v-for="(breadcrumb, index) of breadcrumbs" :key="index">
        <!-- node -->
        <AppNodeBadge
          :node="breadcrumb.node"
          @click.prevent.capture="$router.go(-breadcrumbs.length + index)"
        />

        <!-- relation -->
        <AppRelationBadge :relation="breadcrumb.relation" :vertical="true" />
      </template>

      <!-- ending/current node -->
      <AppNodeBadge :node="node" :link="false" />
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
import { breadcrumbs, updateBreadcrumbs } from "@/global/breadcrumbs";
import { Node } from "@/api/node-lookup";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppRelationBadge from "@/components/AppRelationBadge.vue";

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
