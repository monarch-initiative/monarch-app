<!--
  basic text box input, single line or multi-line
-->

<template>
  <label class="label">
    <div v-if="title" class="title">
      {{ title }}
      <AppIcon v-if="required" icon="asterisk" class="asterisk" />
    </div>
    <div ref="textbox" class="textbox">
      <AppInput
        ref="input"
        class="input"
        v-bind="$attrs"
        :multi="multi"
        :model-value="modelValue"
        :placeholder="placeholder"
        :required="required"
        :debounce="debounce"
        :data-multi="!!multi"
        :data-icon="!!icon"
        @update:model-value="(...args) => $emit('update:modelValue', ...args)"
        @debounce="(...args) => $emit('debounce', ...args)"
        @change="(...args) => $emit('change', ...args)"
        @focus="$emit('focus')"
        @blur="$emit('blur')"
      />
      <div v-if="!modelValue" class="icon">
        <AppIcon v-if="icon" :icon="icon" />
      </div>
      <AppButton
        v-if="modelValue"
        v-tooltip="'Clear text'"
        class="icon"
        icon="times"
        design="small"
        @click.capture.stop="clear"
      />
    </div>
    <div v-if="description" class="description">{{ description }}</div>
  </label>
</template>

<script lang="ts">
export default {
  inheritAttrs: false,
};
</script>

<script setup lang="ts">
import { ref } from "vue";
import AppInput from "./AppInput.vue";

type Props = {
  /** two-way bound text state */
  modelValue?: string;
  /** whether field is multi-line */
  multi?: boolean;
  /** optional side icon */
  icon?: string;
  /** placeholder string when nothing typed in */
  placeholder?: string;
  /** name of field, shown above box */
  title?: string;
  /** description of field, shown below box */
  description?: string;
  /** whether field is required */
  required?: boolean;
  /** delay for debounce in ms */
  debounce?: number;
};

defineProps<Props>();

type Emits = {
  /** two-way bound text state */
  (event: "update:modelValue", value: string): void;
  /** when user types in box, after some delay */
  (event: "debounce", value: string): void;
  /** when user "commits" change (pressing enter, blurring, etc) */
  (event: "change", value: string): void;
  /** when input focused */
  (event: "focus"): void;
  /** when input blurred */
  (event: "blur"): void;
};

const emit = defineEmits<Emits>();

/** element reference */
const textbox = ref();
/** element reference */
const input = ref();

/** clear box */
function clear() {
  input.value.input.value = "";
  input.value.input.dispatchEvent(new Event("input"));
  emit("change", "");
}

/** allow parent to access ref */
defineExpose({ textbox });
</script>

<style lang="scss" scoped>
.label {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  --height: 40px;
}

.title {
  text-align: left;
  font-weight: 500;
}

.asterisk {
  position: relative;
  top: -5px;
  left: 5px;
  color: $error;
  font-size: 0.7rem;
}

.description {
  color: $dark-gray;
  text-align: left;
  font-size: 0.9rem;
}

.textbox {
  position: relative;
  width: 100%;
}

.icon {
  position: absolute;
  right: 0;
  top: 0;
  width: var(--height);
  height: var(--height);
  display: flex;
  justify-content: center;
  align-items: center;
  color: $gray;
}

.input {
  width: 100%;
  background: $white;
  border: solid 2px $off-black;
  border-radius: $rounded;
  outline: none;
  transition: box-shadow $fast;
}

.input[data-multi="false"] {
  height: var(--height);
  padding: 0 calc(var(--height) * 0.25);
  line-height: $spacing;
}

.input[data-multi="true"] {
  min-width: 100%;
  max-width: 100%;
  min-height: calc(var(--height) * 2);
  height: calc(var(--height) * 4);
  padding: calc(var(--height) * 0.25);
  line-height: $spacing;
}

.input[data-icon="true"] {
  padding-right: calc(var(--height) * 0.85);
}

.input:hover,
.input:focus {
  box-shadow: $outline;
}
</style>
