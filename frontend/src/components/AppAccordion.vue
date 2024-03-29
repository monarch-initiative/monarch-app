<!--
  button with expandable/collapsible content
-->

<template>
  <button
    class="title"
    :aria-label="expanded ? 'Collapse section' : 'Expand section'"
    :aria-expanded="expanded"
    @click="expanded = !expanded"
  >
    <span class="text">
      <span v-if="text">{{ text }}</span>
      <AppIcon v-if="icon" class="icon" :icon="icon" />
    </span>
    <AppIcon :class="['caret', { expanded }]" icon="angle-down" />
  </button>
  <div v-if="expanded" class="content">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

type Props = {
  /** text to show in title button */
  text: string;
  /** icon to show in title button */
  icon?: string;
};

defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** whether accordion is open or not */
const expanded = ref(false);
</script>

<style lang="scss" scoped>
.title {
  width: 100%;
  padding: 10px;
  border-bottom: solid 2px $light-gray;
  border-radius: $rounded;
  font-size: 1.1rem;
  transition: background $fast;

  &:hover {
    background: $light-gray;
  }
}

.text {
  flex-grow: 1;
  text-align: left;
}

.icon {
  margin-left: 10px;
  color: $gray;
}

.content {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 20px;
  gap: 20px;
}

.caret {
  position: relative;
  top: 2px;
  transition: transform $fast;
}

.expanded {
  transform: rotate(-180deg);
}
</style>
