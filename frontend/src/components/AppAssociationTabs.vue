<template>
  <div class="association-tabs">
    <div v-if="hasDirectAssociations" class="tab-item">
      <AppButton
        :info="true"
        :info-tooltip="directTooltip"
        :class="['tab-button', { active: directActive }]"
        :disabled="!hasDirectAssociations"
        :text="directLabel"
        color="none"
        @click="$emit('select', 'direct')"
      />
    </div>

    <div v-if="showAllTab" class="tab-item">
      <AppButton
        :info="true"
        :info-tooltip="inferredTooltip"
        :class="['tab-button', { active: allActive }]"
        :text="inferredLabel"
        color="none"
        @click="$emit('select', 'all')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppButton from "@/components/AppButton.vue";

const props = withDefaults(
  defineProps<{
    hasDirectAssociations: boolean;
    showAllTab: boolean;
    directActive: boolean;
    allActive: boolean;
    directLabel: string;
    inferredLabel: string;
    directTooltip?: string;
    inferredTooltip?: string;
  }>(),
  {
    hasDirectAssociations: true,
    showAllTab: true,
    directActive: true,
    allActive: false,
    directLabel: "Direct",
    inferredLabel: "All",
    directTooltip: undefined,
    inferredTooltip: undefined,
  },
);
defineEmits<{
  (e: "select", which: "direct" | "all"): void;
}>();
</script>

<style scoped lang="scss">
$wrap: 900px;
.association-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25em;
  .tab-button {
    z-index: 0;
    position: relative;
    min-width: 22em;
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 8px 8px 0 0;
    background-color: $light-gray;
    &.active {
      z-index: 1;
      background-color: $theme;
      box-shadow: 0 3px 0 0 $theme;
      color: white;
    }
  }
  :deep(.tab-button) {
    border: none;
    outline: none;
    box-shadow: none;
    &:focus,
    &:hover {
      outline: none;
      box-shadow: none;
    }
  }
}
.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
</style>
