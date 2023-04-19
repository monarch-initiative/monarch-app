<!--
  custom tag select component with type-in async search and chips

  references:
  https://www.w3.org/TR/2021/NOTE-wai-aria-practices-1.2-20211129/examples/combobox/combobox-autocomplete-list.html
  https://vuetifyjs.com/en/components/autocompletes
  https://www.downshift-js.com/use-combobox
-->

<template>
  <div class="select-tags">
    <!-- select box -->
    <div
      :id="`select-${id}`"
      ref="target"
      class="box"
      :data-expanded="expanded"
    >
      <!-- deselect button -->
      <AppButton
        v-for="(option, index) in selected"
        :key="index"
        v-tooltip="`Deselect ${option.id}`"
        design="circle"
        :text="option.name || option.id"
        icon="xmark"
        class="selected"
        :aria-label="`Deselect ${option.id}`"
        @click="deselect(option)"
      />

      <AppFlex h-align="right">
        <!-- input box -->
        <AppInput
          v-model="search"
          v-tooltip="{ content: tooltip, offset: [20, 20] }"
          :placeholder="placeholder"
          class="input"
          role="combobox"
          :aria-label="name"
          :aria-expanded="!!results.options.length"
          :aria-controls="`list-${id}`"
          aria-haspopup="listbox"
          aria-autocomplete="list"
          @focus="open"
          @blur="close"
          @debounce="getResults"
          @keydown="onKeydown"
          @paste="onPaste"
        />

        <div class="controls">
          <!-- copy ids -->
          <AppButton
            v-tooltip="`Copy selected values`"
            design="small"
            icon="copy"
            @click="copy"
          />
          {{ " " }}
          <!-- clear box -->
          <AppButton
            v-tooltip="`Clear selected values`"
            design="small"
            icon="times"
            @click="clear"
          />
        </div>
      </AppFlex>
    </div>

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
          results.options.length && highlighted >= 0
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
          v-for="(option, index) in availableResults"
          :id="`option-${id}-${index}`"
          :key="index"
          v-tooltip="option.tooltip"
          class="option"
          role="option"
          :aria-selected="true"
          :data-highlighted="index === highlighted"
          tabindex="0"
          @click="select(option)"
          @mouseenter.capture="highlighted = index"
          @mousedown.prevent=""
          @focusin="() => null"
          @keydown="() => null"
        >
          <span>
            <AppIcon
              v-if="option.icon"
              :icon="option.icon"
              class="option-icon"
            />
          </span>
          <span
            class="option-label truncate"
            v-html="option.highlight || option.name || option.id"
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
/**
 * Instead of providing a static list of options, you can provide this function
 * that receives the user-typed search string and dynamically returns a list of
 * options to display to user for selection or auto-select.
 */
export type OptionsFunc = (search: string) => Promise<{
  /** List of options to return */
  options: Options;
  /** Whether to auto-select these options, or display to user for selection */
  autoAccept?: boolean;
  /** Snackbar message to show when auto-accepting */
  message?: string;
}>;

export type Options = Array<Option>;

export type Option = {
  /** Unique id used in state of select */
  id: string;
  /** Icon name */
  icon?: string;
  /** Display name */
  name?: string;
  /** Highlighting html */
  highlight?: string;
  /** Info col */
  info?: string;
  /** Tooltip on hover */
  tooltip?: string;
  /**
   * Allows returning multiple options instead when selecting this option, e.g.
   * clicking a gene result and getting/selecting its 8 associated phenotypes
   * instead
   */
  spreadOptions?: () => Promise<Options>;
};
</script>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue";
import { uniqueId, isEqual, uniqBy } from "lodash";
import { wrap } from "@/util/math";
import { snackbar } from "./TheSnackbar.vue";
import { sleep } from "@/util/debug";
import { useFloating, useQuery } from "@/util/composables";
import AppInput from "./AppInput.vue";

type Props = {
  /** Two-way bound selected items state */
  modelValue: Options;
  /** Name of the field */
  name: string;
  /** Placeholder string when nothing typed in */
  placeholder?: string;
  /** Async function that returns list of options to show */
  options: OptionsFunc;
  /** Tooltip when hovering input */
  tooltip?: string;
  /** Description to show below box */
  description?: string;
}

const props = defineProps<Props>();

interface Emits {
  /** Two-way bound selected items state */
  (event: "update:modelValue", value: Options): void;
  /** When an option's spreadOptions func has been called */
  (event: "spreadOptions", option: Option, options: Options): void;
}

const emit = defineEmits<Emits>();

/** Unique id for instance of component */
const id = ref(uniqueId());
/** Array of selected options */
const selected = ref<Options>([]);
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
  search.value = "";
  results.value = { options: [] };
  highlighted.value = -1;
}

/** When user presses key in input */
function onKeydown(event: KeyboardEvent) {
  /** Arrow/home/end keys */
  if (["ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) {
    /** Prevent page scroll */
    event.preventDefault();

    /** Move value up/down */
    let index = highlighted.value;
    if (event.key === "ArrowUp") index--;
    if (event.key === "ArrowDown") index++;
    if (event.key === "Home") index = 0;
    if (event.key === "End") index = availableResults.value.length - 1;

    /** Update highlighted, wrapping beyond 0 or results length */
    highlighted.value = wrap(index, 0, availableResults.value.length - 1);
  }

  /** Backspace key to deselect last-selected option */
  if (event.key === "Backspace") {
    if (search.value === "") deselect();
  }

  /** Enter key to de/select highlighted result */
  if (event.key === "Enter" && highlighted.value >= 0) {
    event.preventDefault();
    select(availableResults.value[highlighted.value]);
  }

  /** Esc key to close dropdown */
  if (event.key === "Escape") close();
}

/** When user pastes text */
async function onPaste() {
  /**
   * Wait for pasted value to take effect but don't use nextTick because by then
   * search.value will be reset
   */
  await sleep();
  /** Immediately auto-accept results */
  await getResults();
}

/** Select an option or array of options */
async function select(options: Option | Options) {
  /** Make array if single option */
  if (!Array.isArray(options)) options = [options];

  /** Array of options to select */
  const toSelect: Options = [];

  for (const option of options) {
    /** Run func to get options to select */
    if (option.spreadOptions) {
      const options = await option.spreadOptions();
      toSelect.push(...options);
      /**
       * Notify parent that dynamic options were added. provide option selected
       * and options added.
       */
      emit("spreadOptions", option, options);
    } else toSelect.push(option);
    /** Otherwise just select option */
  }

  /** Select options */
  selected.value.push(...toSelect);
}

/** Deselect a specific option or last-selected option */
function deselect(option?: Option) {
  if (option)
    selected.value = selected.value.filter((model) => model.id !== option.id);
  else selected.value.pop();
}

/** Clear all selected */
function clear() {
  selected.value = [];
}

/** Copy selected ids to clipboard */
async function copy() {
  await window.navigator.clipboard?.writeText(
    selected.value.map(({ id }) => id).join(",")
  );
  snackbar(`Copied ${selected.value.length} values`);
}

const {
  query: getResults,
  data: results,
  isLoading,
  isError,
} = useQuery(
  /** Get list of results */
  async function () {
    /** Reset highlighted */
    highlighted.value = 0;

    /** Get results */
    return await props.options(search.value);
  },

  /** Default value */
  { options: [] },

  /** On success */
  (result) => {
    if (result.autoAccept) {
      /** Auto select */
      select(result.options);

      /** Display message */
      if (result.message) snackbar(result.message);

      /** Reset */
      close();
    }
  }
);

/** List of unselected results to show */
const availableResults = computed(() =>
  results.value.autoAccept
    ? []
    : results.value.options.filter(
        (option) => !selected.value.find((model) => model.id === option.id)
      )
);

/** Target element */
const target = ref();
/** Dropdown element */
const dropdown = ref();
/** Get dropdown position */
const { calculate, style } = useFloating(target, dropdown, true);
/** Recompute position when length of results changes */
watch([expanded, availableResults], async () => {
  await nextTick();
  if (expanded.value) calculate();
});

/** When model changes */
watch(
  () => props.modelValue,
  () => {
    /** Avoid infinite rerenders */
    if (!isEqual(selected.value, props.modelValue))
      /** Update (de-duplicated) selected value */
      selected.value = uniqBy(props.modelValue, "id");
  },
  { deep: true, immediate: true }
);

/** When selected value changes */
watch(
  selected,
  () => {
    /** Emit (deduplicated) updated model */
    emit("update:modelValue", uniqBy(selected.value, "id"));
  },
  { deep: true }
);

/** When highlighted index changes */
watch(highlighted, () => {
  /** Scroll to highlighted in dropdown */
  document
    .querySelector(`#option-${id.value}-${highlighted.value} > *`)
    ?.scrollIntoView({ block: "nearest" });
});
</script>

<style lang="scss" scoped>
.select-tags {
  position: relative;
  width: 100%;
}

.box {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  width: 100%;
  min-height: 40px;
  padding: 5px 10px;
  background: $white;
  border: solid 2px $off-black;
  border-radius: $rounded;
  outline: none;
  transition: box-shadow $fast;
}

.box:hover,
.box[data-expanded="true"] {
  box-shadow: $outline;
}

.input {
  flex-grow: 1;
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
