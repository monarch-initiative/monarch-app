<!--
  node page overview section. basic, high level information about node.
-->

<template>
  <AppSection>
    <AppHeading icon="lightbulb">Overview</AppHeading>

    <AppDetails>
      <!-- symbol (gene specific) -->
      <AppDetail
        v-if="node.category === 'biolink:Gene'"
        :blank="!node.full_name"
        title="Name"
      >
        <p>{{ node.full_name }}</p>
      </AppDetail>

      <!-- paragraph description -->
      <AppDetail :blank="!node.description" title="Description" :full="true">
        <p
          v-tooltip="'Click to expand'"
          class="description truncate-10"
          tabindex="0"
          v-html="node.description?.trim()"
        ></p>
      </AppDetail>

      <!-- synonyms -->
      <AppDetail
        :blank="!node.synonym?.length"
        title="Also Known As"
        :full="true"
      >
        <p
          class="truncate-2"
          tabindex="0"
          v-html="node.synonym?.join(',\n&nbsp;')"
        ></p>
      </AppDetail>

      <!-- association counts -->
      <AppDetail
        :blank="!node.association_counts"
        title="Association Counts"
        :full="true"
      >
        <AppFlex align-h="left">
          <span v-for="(count, index) in node.association_counts" :key="index">
            {{ count.label }} {{ count.count?.toLocaleString() || 0 }}
          </span>
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import type { Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();
</script>

<style lang="scss" scoped>
.description {
  width: 100%;
  overflow-x: auto;
  white-space: pre-line;
}
</style>
