<!--
  node page overview section. basic, high level information about node.
-->

<template>
  <AppSection>
    <AppHeading icon="lightbulb">Overview</AppHeading>

    <AppDetails>
      <!-- synonyms -->
      <AppDetail :blank="!node.synonym" title="Also Known As">
        <p v-html="node.synonym?.join(',\n&nbsp;')"></p>
      </AppDetail>

      <!-- symbol (gene specific) -->
      <AppDetail
        v-if="node.category === 'biolink:Gene'"
        :blank="!node.full_name"
        title="Name"
      >
        <p>{{ node.full_name }}</p>
      </AppDetail>

      <!-- authors (publication specific) -->
      <AppDetail :blank="!node.provided_by" title="Provided By">
        <p>{{ node.provided_by }}</p>
      </AppDetail>

      <!-- paragraph description -->
      <AppDetail :blank="!node.description" title="Description" :big="true">
        <p
          v-tooltip="'Click to expand'"
          class="description truncate-10"
          tabindex="0"
          v-html="node.description?.trim()"
        ></p>
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
