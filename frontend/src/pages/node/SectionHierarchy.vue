<!--
  node page hierarchy section. super/sub/equivalent classes of current node.
-->

<template>
  <AppSection
    v-if="node.category !== 'biolink:Gene'"
    width="full"
    alignment="left"
    class="inset"
    design="bare"
  >
    <AppHeading icon="sitemap">Hierarchy</AppHeading>

    <AppDetails>
      <!-- nodes that are "parents" of node -->
      <AppDetail
        title="Super-classes"
        icon="angle-up"
        :blank="!node.node_hierarchy?.super_classes.length"
        :full="true"
        :v-tooltip="`Nodes that are &quot;parents&quot; of this node`"
      >
        <AppFlex class="flex" align-h="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in node.node_hierarchy?.super_classes"
            :key="index"
            :node="_class"
            :breadcrumbs="[
              {
                node: toBreadcrumbNode(node),
                association: {
                  predicate: 'is super class of',
                  direction: AssociationDirectionEnum.incoming,
                },
              },
            ]"
          />
        </AppFlex>
      </AppDetail>

      <!-- nodes that are "children" of node -->
      <AppDetail
        :title="`Sub-classes (${node.node_hierarchy?.sub_classes.length})`"
        icon="angle-down"
        :blank="!node.node_hierarchy?.sub_classes.length"
        :full="true"
        :v-tooltip="`Nodes that are &quot;children&quot; of this node`"
      >
        <AppFlex class="flex" align-h="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in node.node_hierarchy?.sub_classes"
            :key="index"
            :node="_class"
            :breadcrumbs="[
              {
                node: toBreadcrumbNode(node),
                association: { predicate: 'is sub class of' },
              },
            ]"
          />
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { AssociationDirectionEnum, type Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { toBreadcrumbNode } from "@/global/breadcrumbs";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();
</script>

<style lang="scss" scoped>
.flex {
  column-gap: 20px !important;
}
</style>
