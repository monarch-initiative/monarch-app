<!--
  raw, un-styled multi or single line input component with debounce
-->

<template>
  <component
    :is="multi ? 'textarea' : 'input'"
    ref="input"
    :value="modelValue"
    @focus="onFocus"
    @blur="onBlur"
    @input="onInput"
    @change="onChange"
  >
  </component>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref } from "vue";
import { debounce as _debounce } from "lodash";

type Props = {
  /** two-way bound text state */
  modelValue?: string;
  /** whether field is multi-line */
  multi?: boolean;
  /** delay for debounce in ms */
  debounce?: number;
};

const props = defineProps<Props>();

type Emits = {
  /** two-way bound text state */
  "update:modelValue": [string];
  /** when user types in box, after some delay */
  debounce: [string];
  /** when user "commits" change (pressing enter, blurring, etc) */
  change: [string];
  /** when input focused */
  focus: [];
  /** when input blurred */
  blur: [];
};

const emit = defineEmits<Emits>();

/** element reference */
const input = ref<null | InstanceType<typeof >>(null);

/** when user focuses box */
function onFocus() {
  emit("focus");
}

/** when user blurs box */
function onBlur() {
  emit("blur");
}

/** when user types in box */
function onInput() {
  /** check if component still mounted */
  if (!input.value) return;

  emit("update:modelValue", input.value?.value);
  onDebounce(input.value?.value);
}

/** when user types in box, after some delay */
const onDebounce = _debounce(function (value: string) {
  emit("debounce", value);
}, props.debounce || 500);

/** when user "commits" change (pressing enter, blurring, etc) */
async function onChange() {
  /** check if component still mounted */
  if (!input.value) return;

  emit("change", input.value?.value);
}

/** allow parent to access ref */
defineExpose({ input });

/** cancel any pending debounce calls */
onBeforeUnmount(onDebounce.cancel);
</script>
