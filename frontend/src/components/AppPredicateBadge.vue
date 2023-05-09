<!--
  an icon, text, and link for a predicate between nodes in the knowledge graph
-->

<template>
    <span class="relation">
      <AppIcon class="arrow" :icon="`arrow-${arrowDirection}-long`" />
      <AppLink :to="predicate.id" :no-icon="true">{{
        startCase(predicate.name)
      }}</AppLink>
      <AppIcon class="arrow" :icon="`arrow-${arrowDirection}-long`" />
    </span>
  </template>
  
  <script setup lang="ts">
  import { computed } from "vue";
  import { startCase } from "lodash";
  
  type Props = {
    /** current relation */
    predicate: {id: string, name: string};
    /** whether to display arrows vertically */
    vertical?: boolean;
  };
  
  const props = defineProps<Props>();
  
  /** direction of arrows */
  const arrowDirection = computed(() => {
    if (props.vertical) {
      if (props.predicate) return "up";
      else return "down";
    } 
    else {
      if (props.predicate) return "left";
      else return "right";
    }
  });
  </script>
  
  <style lang="scss" scoped>
  .relation {
    white-space: nowrap;
  
    & > * {
      white-space: normal;
      overflow-wrap: anywhere;
    }
  }
  
  .arrow {
    color: $gray;
  
    &:first-child {
      margin-right: 0.5em;
    }
  
    &:last-child {
      margin-left: 0.5em;
    }
  }
  </style>
  