<!--
  custom dropdown select component with type-in async search

  references:
  https://www.w3.org/TR/2021/NOTE-wai-aria-practices-1.2-20211129/examples/combobox/combobox-autocomplete-list.html
  https://vuetifyjs.com/en/components/autocompletes
  https://www.downshift-js.com/use-combobox
-->

<template>
  <div class="select-autocomplete">
    <!-- select box -->
    <AppTextbox
      :id="`select-${id}`"
      ref="target"
      v-model="search"
      class="box"
      icon="search"
      role="combobox"
      :placeholder="placeholder"
      :debounce="200"
      :aria-label="name"
      :aria-expanded="!!results.length"
      :aria-controls="`list-${id}`"
      aria-haspopup="listbox"
      aria-autocomplete="list"
      @focus="onFocus"
      @blur="onBlur"
      @debounce="onDebounce"
      @change="onChange"
      @keydown="onKeydown"
    />

    <!-- dropdown -->
    <Teleport to="body">
      <div
        v-if="expanded"
        :id="`list-${id}`"
        ref="dropdown"
        class="list"
        role="listbox"
        tabindex="0"
        :aria-labelledby="`select-${id}`"
        :aria-activedescendant="
          results.length && highlighted >= 0
            ? `option-${id}-${highlighted}`
            : undefined
        "
        :style="style"
      >
        <!-- status -->
        <AppStatus v-if="isLoading" code="loading" role="option"
          >Loading results</AppStatus
        >
        <AppStatus v-if="isError" code="error" role="option"
          >Error loading results</AppStatus
        >

        <!-- list of results -->
        <div
          v-for="(option, index) in results"
          :id="`option-${id}-${index}`"
          :key="index"
          v-tooltip="option.tooltip"
          class="option"
          role="option"
          :aria-selected="true"
          :data-highlighted="index === highlighted"
          tabindex="0"
          @click.prevent="() => select(option.name)"
          @mouseenter.capture="highlighted = index"
          @mousedown.prevent=""
          @focusin="() => null"
          @keydown="() => null"
        >
          <AppIcon v-if="option.icon" :icon="option.icon" class="option-icon" />
          <span
            class="option-label truncate"
            v-html="option.highlight || option.name"
          >
          </span>
          <span v-if="option.info" class="option-info truncate">{{
            option.info
          }}</span>
        </div>
      </div>
    </Teleport>

    <!-- description -->
    <div v-if="description" class="description">{{ description }}</div>
  </div>
</template>

<script lang="ts">
export type OptionsFunc = (search: string) => Promise<Options>;

export type Options = Array<Option>;

export type Option = {
  /** Icon name */
  icon?: string;
  /** Display name */
  name: string;
  /** Highlighting html */
  highlight?: string;
  /** Info col */
  info?: string;
  /** Tooltip on hover */
  tooltip?: string;
};
</script>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { uniqueId } from "lodash";
import { useFloating, useQuery } from "@/util/composables";
import { wrap } from "@/util/math";
import AppTextbox from "./AppTextbox.vue";

type Props = {
  /** Two-way bound search state */
  modelValue?: string;
  /** Name of the field */
  name: string;
  /** Placeholder string when nothing typed in */
  placeholder?: string;
  /** Async function that returns list of options to show */
  options: OptionsFunc;
  /** Description to show below box */
  description?: string;
};

const props = defineProps<Props>();

interface Emits {
  /** Two-way bound search state */
  (event: "update:modelValue", value: string): void;
  /** When input focused */
  (event: "focus"): void;
  /** When input value change "submitted"/"committed" by user */
  (event: "change", value: string): void;
  /** When user wants to delete an entry */
  (event: "delete", value: string): void;
}

const emit = defineEmits<Emits>();

/** Unique id for instance of component */
const id = ref(uniqueId());
/** Currently searched text */
const search = ref("");
/** Index of option that is highlighted */
const highlighted = ref(0);
/** Whether input box focused and dropdown expanded */
const expanded = ref(false);

/** Open results dropdown */
async function open() {
  expanded.value = true;
  highlighted.value = -1;
  await getResults();
}

/** Close results dropdown */
function close() {
  expanded.value = false;
  highlighted.value = -1;
  results.value = [];
}

/** When user focuses box */
function onFocus() {
  emit("focus");
  open();
}

/** When user blurs box */
async function onBlur() {
  close();
}

/** When user types some text, after a delay */
async function onDebounce() {
  await getResults();
}

/** When user "commits" change to value, e.g. pressing enter, de-focusing, etc */
function onChange(value: string) {
  select(value);
}

/** When user presses key in input */
async function onKeydown(event: KeyboardEvent) {
  /** Reopen if previously submitted */
  expanded.value = true;

  /** Arrow/home/end keys */
  if (["ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) {
    /** Prevent page scroll */
    event.preventDefault();

    /** Move value up/down */
    let index = highlighted.value;
    if (event.key === "ArrowUp") index--;
    if (event.key === "ArrowDown") index++;
    if (event.key === "Home") index = 0;
    if (event.key === "End") index = results.value.length - 1;

    /** Update highlighted, wrapping beyond 0 or results length */
    highlighted.value = wrap(index, 0, results.value.length - 1);
  }

  /** Enter key to select highlighted result */
  if (event.key === "Enter" && highlighted.value >= 0) {
    event.stopPropagation();
    select(results.value[highlighted.value].name);
  }

  /** Delete key to delete the highlighted result */
  if (event.key === "Delete" && event.shiftKey) {
    emit("delete", results.value[highlighted.value].name);
    await getResults();
  }

  /** Esc key to close dropdown */
  if (event.key === "Escape") close();
}

/** Select an option */
async function select(value: string) {
  search.value = value;
  emit("change", value);
  close();
}

const {
  query: getResults,
  data: results,
  isLoading,
  isError,
} = useQuery(
  /** Get list of results */
  async function () {
    /** Get results */
    return await props.options(search.value);
  },

  /** Default value */
  []
);

/** Target element */
const target = ref();
/** Dropdown element */
const dropdown = ref();
/** Get dropdown position */
const { calculate, style } = useFloating(
  computed(() => target.value?.textbox),
  dropdown,
  true
);
/** Recompute position when length of results changes */
watch([expanded, results], async () => {
  await nextTick();
  if (expanded.value) calculate();
});

/** When model changes, update search */
watch(
  () => props.modelValue,
  () => (search.value = props.modelValue || ""),
  { immediate: true }
);

/** When search changes, update model */
watch(search, () => {
  emit("update:modelValue", search.value);
});

/** When highlighted index changes */
watch(highlighted, () => {
  /** Scroll to highlighted in dropdown */
  document
    .querySelector(`#option-${id.value}-${highlighted.value} > *`)
    ?.scrollIntoView({ block: "nearest" });
});
</script>

<style lang="scss" scoped>
.select-autocomplete {
  position: relative;
  width: 100%;
}

.box {
  width: 100%;
  min-height: 40px;
}

.selected {
  min-height: unset !important;
  font-size: 0.9rem;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
}

.list {
  max-height: 300px;
  overflow-x: auto;
  overflow-y: auto;
  background: $white;
  box-shadow: $shadow;
  z-index: 12;
}

.option {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background $fast;
}

.option[data-highlighted="true"] {
  background: $light-gray;
}

.option-icon {
  color: $off-black;
}

.option-label {
  flex-grow: 1;
  justify-content: flex-start;
}

.option-info {
  justify-content: flex-end;
  color: $gray;
}

.description {
  margin-top: 10px;
  color: $dark-gray;
  font-size: 0.9rem;
}
</style>
