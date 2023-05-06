<!--
  node page hierarchy section. super/sub/equivalent classes of current node.
-->

<template>
  <AppSection>
    <AppHeading icon="sitemap">Hierarchy</AppHeading>

    <!-- status -->
    <AppStatus v-if="isLoading" code="loading"
      >Loading hierarchy data</AppStatus
    >
    <AppStatus v-else-if="isError" code="error"
      >Error loading hierarchy data</AppStatus
    >

    <AppDetails v-else>
      <!-- nodes that are "parents" of node -->
      <AppDetail
        title="Super-classes"
        icon="angle-up"
        :blank="!hierarchy.super_classes?.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;parents&quot; of this node`"
      >
        <AppFlex class="flex" h-align="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in hierarchy.super_classes"
            :key="index"
            :node="_class"
            :breadcrumb="{ node }"
          />
          <!-- :breadcrumb="{ node, relation: _class.relation }" -->
        </AppFlex>
      </AppDetail>

      <!-- nodes that are "siblings" of node -->
      <AppDetail
        title="Equivalent classes"
        icon="equals"
        :blank="!hierarchy.equivalent_classes?.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;siblings&quot; of this node`"
      >
        <AppFlex class="flex" h-align="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in hierarchy.equivalent_classes"
            :key="index"
            :node="_class"
            :breadcrumb="{ node }"
          />
        </AppFlex>
      </AppDetail>

      <!-- nodes that are "children" of node -->
      <AppDetail
        title="Sub-classes"
        icon="angle-down"
        :blank="!hierarchy.sub_classes?.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;children&quot; of this node`"
      >
        <AppFlex class="flex" h-align="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in hierarchy.sub_classes"
            :key="index"
            :node="_class"
            :breadcrumb="{ node }"
          />
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useRoute } from "vue-router";
import type { Node, NodeHierarchy } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { useQuery } from "@/util/composables";

/** route info */
const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

// function returning node hierarchy
const {
  query: getHierarchy,
  data: hierarchy,
  isLoading,
  isError,
} = useQuery(
  function (): Promise<NodeHierarchy> {
    const h = props.node.node_hierarchy;
    if (h) {
      return Promise.resolve(h);
    } else {
      return Promise.reject("No node hierarchy data");
    }
  },

  /** default value */
  { super_classes: [], equivalent_classes: [], sub_classes: [] }
);

/** when path (not hash or query) changed, get new node data */
watch(
  [() => route.path, () => props.node.id, () => props.node.category],
  getHierarchy,
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.flex {
  column-gap: 20px !important;
}
</style>
