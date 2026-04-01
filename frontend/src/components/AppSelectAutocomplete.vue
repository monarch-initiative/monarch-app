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
      ref="anchor"
      v-model="search"
      class="box"
      icon="magnifying-glass"
      role="combobox"
      :placeholder="placeholder"
      :debounce="200"
      :aria-label="name"
      :aria-expanded="!!results.length"
      :aria-controls="`list-${id}`"
      aria-haspopup="listbox"
      aria-autocomplete="list"
      autocomplete="off"
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
          :class="[
            'option',
            { highlighted: index === highlighted, special: option.special },
          ]"
          role="option"
          :aria-selected="true"
          tabindex="0"
          @click.prevent="() => select(option)"
          @mousedown.prevent=""
          @focusin="() => null"
          @keydown="() => null"
        >
          <AppIcon v-if="option.icon" :icon="option.icon" class="option-icon" />
          <span
            class="option-label truncate"
            v-html="option.highlight || option.label"
          >
          </span>
          <span v-if="option.info" class="option-info truncate">{{
            option.info
          }}</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script lang="ts">
export type OptionsFunc = (search: string) => Promise<Options>;

export type Options = Option[];

export type Option = {
  /** icon name */
  icon?: string;
  /** display label */
  label: string;
  /** unique id */
  id?: string;
  /** highlighting html */
  highlight?: string;
  /** info col */
  info?: string;
  /** tooltip on hover */
  tooltip?: string;
  /** whether option is "special" (gets styled differently) */
  special?: boolean;
};
</script>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { uniqueId } from "lodash";
import { useFloating } from "@/composables/use-floating";
import { useQuery } from "@/composables/use-query";
import { wrap } from "@/util/math";
import AppTextbox from "./AppTextbox.vue";

type Props = {
  /** two-way bound search state */
  modelValue?: string;
  /** name of the field */
  name: string;
  /** placeholder string when nothing typed in */
  placeholder?: string;
  /** async function that returns list of options to show */
  options: OptionsFunc;
  /** description to show below box */
  description?: string;
};

const props = defineProps<Props>();

type Emits = {
  /** two-way bound search state */
  "update:modelValue": [string];
  /** when input focused */
  focus: [];
  /** when input value change "submitted"/"committed" by user */
  change: [string | Option, string];
  /** when user wants to delete an entry */
  delete: [Option];
};

const emit = defineEmits<Emits>();

/** unique id for instance of component */
const id = uniqueId();
/** currently searched text */
const search = ref("");
/** index of option that is highlighted (keyboard controls) */
const highlighted = ref(0);
/** whether input box focused and dropdown expanded */
const expanded = ref(false);

/** open results dropdown */
async function open() {
  expanded.value = true;
  highlighted.value = -1;
  await runGetResults();
}

/** close results dropdown */
function close() {
  expanded.value = false;
  highlighted.value = -1;
  results.value = [];
}

/** when user focuses box */
function onFocus() {
  emit("focus");
  open();
}

/** when user blurs box */
async function onBlur() {
  close();
}

/** when user types some text, after a delay */
async function onDebounce() {
  await runGetResults();
}

/** ignore next child input box change event */
let ignoreChange = false;

/** when user "commits" change to value, e.g. pressing enter, de-focusing, etc */
async function onChange(value: string) {
  if (!ignoreChange) select(value);
  ignoreChange = false;
}

/** when user presses key in input */
async function onKeydown(event: KeyboardEvent) {
  /** reopen if previously submitted */
  expanded.value = true;

  /** arrow/home/end keys */
  if (["ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) {
    /** prevent page scroll */
    event.preventDefault();

    /** move value up/down */
    let index = highlighted.value;
    if (event.key === "ArrowUp") index--;
    if (event.key === "ArrowDown") index++;
    if (event.key === "Home") index = 0;
    if (event.key === "End") index = results.value.length - 1;

    /** update highlighted, wrapping beyond 0 or results length */
    highlighted.value = wrap(index, 0, results.value.length - 1);
  }

  /** enter key to select highlighted result */
  if (event.key === "Enter" && highlighted.value >= 0) {
    select(results.value[highlighted.value]);
  }

  /** delete key to delete the highlighted result */
  if (event.key === "Delete" && event.shiftKey) {
    emit("delete", results.value[highlighted.value]);
    await runGetResults();
  }

  /** esc key to close dropdown */
  if (event.key === "Escape") close();
}

/** select an option */
async function select(value: string | Option) {
  /** ignore next child input box change event triggered by enter press */
  ignoreChange = true;
  emit("change", value, search.value);
  search.value = typeof value === "string" ? value : value.label;
  close();
}

const {
  query: runGetResults,
  data: results,
  isLoading,
  isError,
} = useQuery(
  /** get list of results */
  async function () {
    /** get results */
    return await props.options(search.value);
  },

  /** default value */
  [],
);

/** anchor element */
const anchor = ref<InstanceType<typeof AppTextbox>>();
/** dropdown element */
const dropdown = ref<HTMLDivElement>();
/** get dropdown position */
const { calculate, style } = useFloating(
  computed(() => anchor.value?.textbox),
  dropdown,
  true,
);
/** recompute position when length of results changes */
watch([expanded, results], async () => {
  await nextTick();
  if (expanded.value) calculate();
});

/** when model changes, update search */
watch(
  () => props.modelValue,
  () => (search.value = props.modelValue || ""),
  { immediate: true },
);

/** when search changes, update model */
watch(search, () => {
  emit("update:modelValue", search.value);
});

/** when highlighted index changes */
watch(highlighted, () => {
  /** scroll to highlighted in dropdown */
  document
    .querySelector(`#option-${id}-${highlighted.value} > *`)
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
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.list {
  z-index: 1020;
  max-height: 300px;
  overflow-x: auto;
  overflow-y: auto;
  background: $white;
  box-shadow: $shadow;
}

.option {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 10px;
  gap: 10px;
  cursor: pointer;
  transition: background $fast;
}

.option:hover,
.option.highlighted {
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

.special {
  font-weight: 500;
}
</style>
