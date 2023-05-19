<!--
  node page title section, at top, below header. basic identifying info of node.
-->

<template>
  <AppSection design="fill" class="section">
    <AppFlex dir="column" gap="small">
      <AppHeading
        class="heading"
        :icon="`category-${node.category_label || 'unknown'}`"
      >
        {{ node.name }}
      </AppHeading>
      <AppFlex>
        <AppButton
          v-tooltip="'The category/type of this node'"
          design="small"
          color="secondary"
          :text="node.category_label || 'Unknown'"
        />
        <AppButton
          v-tooltip="'The ID of this node. Click to copy.'"
          design="small"
          color="secondary"
          icon="hashtag"
          :text="node.id"
          :copy="true"
        />
      </AppFlex>
    </AppFlex>
  </AppSection>
</template>

<script setup lang="ts">
import type { Node } from "@/api/model";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();
</script>

<style lang="scss" scoped>
.section {
  padding-top: 30px !important;
  padding-bottom: 30px !important;
}

.button {
  color: $off-black !important;
}

.heading {
  font-size: 1.2rem;
}

.original-id {
  color: $dark-gray;
  font-style: italic;
  font-size: 0.9rem;
}
</style>
