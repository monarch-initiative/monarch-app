<template>
  <AppSection width="full" alignment="left" design="bare">
    <AppHeading icon="location-dot">Breadcrumbs</AppHeading>

    <template v-if="breadcrumbs.length">
      <span
        >How you got to <AppNodeBadge :node="node" /> through the Monarch
        knowledge graph:</span
      >

      <AppFlex direction="col">
        <template v-for="(breadcrumb, index) of _breadcrumbs" :key="index">
          <!-- node -->
          <AppNodeBadge
            v-tooltip="`Go ${-breadcrumb.back} step(s) back`"
            :node="breadcrumb.node"
            :style="{ opacity: breadcrumb.noEntry ? 0.5 : 1 }"
            @click.prevent.capture="$router.go(breadcrumb.back)"
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
        icon="xmark"
        text="Clear"
        design="small"
        @click="clear"
      />
    </template>

    <template v-else>
      <p class="gray">
        As you navigate to new nodes from this page, the path you traveled
        through the KG will be shown here. Try clicking on a node in the
        hierarchy or associations sections.
      </p>
    </template>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
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

/**
 * breadcrumbs, plus computed "back" prop to tell how many history steps to go
 * back when clicked
 */
const _breadcrumbs = computed(() => {
  let back =
    -breadcrumbs.value.filter((breadcrumb) => !breadcrumb.noEntry).length - 1;
  return breadcrumbs.value.map((breadcrumb) => ({
    ...breadcrumb,
    back: breadcrumb.noEntry ? back : ++back,
  }));
});

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

.gray {
  color: $dark-gray;
}
</style>
