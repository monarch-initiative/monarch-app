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
        :blank="!hierarchy.superClasses.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;parents&quot; of this node`"
      >
        <AppFlex class="flex" h-align="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in hierarchy.superClasses"
            :key="index"
            :node="_class"
            :breadcrumb="{ node, relation: _class.relation }"
          />
        </AppFlex>
      </AppDetail>

      <!-- nodes that are "siblings" of node -->
      <AppDetail
        title="Equivalent classes"
        icon="equals"
        :blank="!hierarchy.equivalentClasses.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;siblings&quot; of this node`"
      >
        <AppFlex class="flex" h-align="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in hierarchy.equivalentClasses"
            :key="index"
            :node="_class"
            :breadcrumb="{ node, relation: _class.relation }"
          />
        </AppFlex>
      </AppDetail>

      <!-- nodes that are "children" of node -->
      <AppDetail
        title="Sub-classes"
        icon="angle-down"
        :blank="!hierarchy.subClasses.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;children&quot; of this node`"
      >
        <AppFlex class="flex" h-align="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in hierarchy.subClasses"
            :key="index"
            :node="_class"
            :breadcrumb="{ node, relation: _class.relation }"
          />
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useRoute } from "vue-router";
import { getHierarchy } from "@/api/node-hierarchy";
import type { Node } from "@/api/node-lookup";
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

/** get node hierarchy data */
const {
  query: getData,
  data: hierarchy,
  isLoading,
  isError,
} = useQuery(
  async function () {
    return await getHierarchy(props.node.id, props.node.category);
  },

  /** default value */
  { superClasses: [], equivalentClasses: [], subClasses: [] }
);

/** when path (not hash or query) changed, get new node data */
watch(
  [() => route.path, () => props.node.id, () => props.node.category],
  getData,
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.flex {
  column-gap: 20px !important;
}
</style>
