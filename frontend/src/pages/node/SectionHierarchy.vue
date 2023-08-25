<!--
  node page hierarchy section. super/sub/equivalent classes of current node.
-->

<template>
  <AppSection>
    <AppHeading icon="sitemap">Hierarchy</AppHeading>

    <AppDetails>
      <!-- nodes that are "parents" of node -->
      <AppDetail
        title="Super-classes"
        icon="angle-up"
        :blank="!node.node_hierarchy?.super_classes.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;parents&quot; of this node`"
      >
        <AppFlex class="flex" align-h="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in node.node_hierarchy?.super_classes"
            :key="index"
            :node="_class"
            :breadcrumb="{
              node,
              association: {
                predicate: 'is super class of',
                direction: AssociationDirectionEnum.incoming,
              },
            }"
          />
        </AppFlex>
      </AppDetail>

      <!-- nodes that are "siblings" of node -->
      <AppDetail
        title="Equivalent classes"
        icon="equals"
        :blank="!node.node_hierarchy?.equivalent_classes.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;siblings&quot; of this node`"
      >
        <AppFlex class="flex" align-h="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in node.node_hierarchy?.equivalent_classes"
            :key="index"
            :node="_class"
            :breadcrumb="{
              node,
              association: { predicate: 'is equivalent class of' },
            }"
          />
        </AppFlex>
      </AppDetail>

      <!-- nodes that are "children" of node -->
      <AppDetail
        title="Sub-classes"
        icon="angle-down"
        :blank="!node.node_hierarchy?.sub_classes.length"
        :big="true"
        :v-tooltip="`Nodes that are &quot;children&quot; of this node`"
      >
        <AppFlex class="flex" align-h="left" gap="small">
          <AppNodeBadge
            v-for="(_class, index) in node.node_hierarchy?.sub_classes"
            :key="index"
            :node="_class"
            :breadcrumb="{
              node,
              association: { predicate: 'is sub class of' },
            }"
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
