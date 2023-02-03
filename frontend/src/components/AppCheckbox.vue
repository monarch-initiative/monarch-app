<!--
  checkbox with arbitrary content (slot) and icon
-->

<template>
  <label class="checkbox">
    <input
      type="checkbox"
      class="input"
      :checked="modelValue"
      @change="onChange"
    />
    <AppIcon class="check" :icon="modelValue ? 'square-check' : 'square'" />
    <span v-if="text">{{ text }}</span>
    <AppIcon v-if="icon" class="icon" :icon="icon" />
  </label>
</template>

<script setup lang="ts">
interface Props {
  /** two-way bound checked state */
  modelValue?: boolean;
  /** text to show in label */
  text: string;
  /** icon to show in label */
  icon?: string;
}

defineProps<Props>();

interface Emits {
  /** two-way bound checked state */
  (event: "update:modelValue", checked: boolean): void;
}

const emit = defineEmits<Emits>();

/** when checkbox value changes */
function onChange(event: Event) {
  emit("update:modelValue", (event?.target as HTMLInputElement).checked);
}
</script>

<style lang="scss" scoped>
.checkbox {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: $rounded;
  cursor: pointer;
  transition: background $fast;

  .check {
    color: $theme;
    font-size: 1.2rem;
  }

  .icon {
    color: $gray;
  }

  &:focus-within,
  &:hover {
    background: $light-gray;
  }

  .input {
    position: absolute;
  }
}
</style>
