<!--
  custom single select

  references:
  https://www.w3.org/TR/2021/NOTE-wai-aria-practices-1.2-20211129/examples/combobox/combobox-select-only.html
  https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/listbox_role
  https://vuetifyjs.com/en/components/selects/
  https://www.downshift-js.com/use-select
-->

<template>
  <div class="select-single">
    <!-- select button box -->
    <button
      :id="`select-${id}`"
      ref="target"
      class="box"
      :aria-label="name"
      :aria-expanded="expanded"
      :aria-controls="`list-${id}`"
      aria-haspopup="listbox"
      tabindex="0"
      @click="onClick"
      @keydown="onKeydown"
      @blur="onBlur"
    >
      <AppIcon v-if="modelValue?.icon" :icon="modelValue?.icon" />
      <span class="box-label">{{ modelValue?.name || modelValue?.id }}</span>
      <AppIcon :icon="expanded ? 'angle-up' : 'angle-down'" />
    </button>

    <!-- options list -->
    <Teleport to="body">
      <div
        v-if="expanded"
        :id="`list-${id}`"
        ref="dropdown"
        class="list"
        role="listbox"
        :aria-labelledby="`select-${id}`"
        :aria-activedescendant="`option-${id}-${highlighted}`"
        tabindex="0"
        :style="style"
      >
        <div
          v-for="(option, index) in options"
          :id="`option-${id}-${index}`"
          :key="index"
          v-tooltip="option.tooltip"
          class="option"
          role="option"
          :aria-selected="selected === index"
          :data-selected="selected === index"
          :data-highlighted="index === highlighted"
          tabindex="0"
          @click="selected = index"
          @mouseenter.capture="highlighted = index"
          @mousedown.prevent=""
          @focusin="() => null"
          @keydown="() => null"
        >
          <AppIcon v-if="option.icon" :icon="option.icon" class="option-icon" />
          <span class="option-label truncate">
            {{ option.name || option.id }}
          </span>
          <span v-if="option.count" class="option-count">{{
            option.count
          }}</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script lang="ts">
export type Option = {
  /** Unique id used in state of select */
  id: string;
  /** Icon name */
  icon?: string;
  /** Display name */
  name?: string;
  /** Count col */
  count?: number;
  /** Tooltip on hover */
  tooltip?: string;
};

export type Options = Array<Option>;
</script>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import { uniqueId } from "lodash";
import { wrap } from "@/util/math";
import { useFloating } from "@/util/composables";

type Props = {
  /** Two-way bound selected item state */
  modelValue?: Option;
  /** Name of the field */
  name: string;
  /** List of options to show */
  options: Options;
};

const props = defineProps<Props>();

interface Emits {
  /** Two-way bound selected item state */
  (event: "update:modelValue", value: Option): void;
}

const emit = defineEmits<Emits>();

/** Unique id for instance of component */
const id = ref(uniqueId());
/** Whether dropdown is open */
const expanded = ref(false);
/** Index of option that is selected */
const selected = ref(getSelected());
/** Index of option that is highlighted */
const highlighted = ref(0);

/** Target element */
const target = ref();
/** Dropdown element */
const dropdown = ref();
/** Get dropdown position */
const { calculate, style } = useFloating(target, dropdown);
/** Recompute position after opened */
watch(expanded, async () => {
  await nextTick();
  if (expanded.value) calculate();
});

/** Open dropdown */
function open() {
  expanded.value = true;
  /** Auto highlight selected option */
  highlighted.value = selected.value;
}

/** Close dropdown */
function close() {
  expanded.value = false;
}

/** When button clicked */
function onClick() {
  /** Toggle dropdown */
  expanded.value ? close() : open();
  /** https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#clicking_and_focus */
  (document.querySelector(`#select-${id.value}`) as HTMLElement)?.focus();
}

/** When button blurred */
function onBlur() {
  close();
}

/** When user presses key on button */
function onKeydown(event: KeyboardEvent) {
  /** Arrow/home/end keys */
  if (["ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) {
    /** Prevent page scroll */
    event.preventDefault();

    /**
     * If dropdown open, control highlighted option. if dropdown closed, control
     * selected option.
     */
    let index = expanded.value ? highlighted.value : selected.value;

    /** Move value up/down */
    if (event.key === "ArrowUp") index--;
    if (event.key === "ArrowDown") index++;
    if (event.key === "Home") index = 0;
    if (event.key === "End") index = props.options.length - 1;

    /** Update value, wrapping beyond 0 or options length */
    index = wrap(index, 0, props.options.length - 1);
    if (expanded.value) highlighted.value = index;
    else selected.value = index;
  }

  /** Enter key to select highlighted option */
  if (expanded.value && (event.key === "Enter" || event.key === " ")) {
    /** Prevent browser re-clicking open button */
    event.preventDefault();
    selected.value = highlighted.value;
  }

  /** Esc key to close dropdown */
  if (expanded.value && event.key === "Escape") close();
}

/** Get selected option index from model */
function getSelected() {
  return props.options.findIndex(
    (option) => option?.id === props.modelValue?.id
  );
}

/** When model changes */
watch(
  () => props.modelValue,
  () =>
    /** Update selected index */
    (selected.value = getSelected())
);

/** When selected index changes */
watch(selected, () => {
  /** Emit updated model */
  emit("update:modelValue", props.options[selected.value]);
  close();
});

/** When highlighted index changes */
watch(highlighted, () =>
  /** Scroll to highlighted in dropdown */
  document
    .querySelector(`#option-${id.value}-${highlighted.value}`)
    ?.scrollIntoView({ block: "nearest" })
);

/** Auto-select first option as fallback */
watch(
  () => props.options,
  () => {
    if (selected.value === -1 && props.options.length) selected.value = 0;
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.select-single {
  position: relative;
  max-width: 100%;
}

.box {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 5px 10px;
  border-radius: $rounded;
  background: $light-gray;
}

.box-label {
  flex-grow: 1;
  text-align: left;
}

.list {
  position: fixed;
  max-width: 90vw;
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
  text-align: left;
  white-space: nowrap;
  cursor: pointer;
  transition: background $fast;
}

.option[data-selected="true"] {
  background: $theme-light;
}

.option[data-highlighted="true"] {
  background: $light-gray;
}

.option-icon {
  color: $off-black;
  font-size: 1.2rem;
}

.option-label {
  flex-grow: 1;
  justify-content: flex-start;
  overflow-x: hidden;
}

.option-count {
  justify-content: flex-end;
  color: $gray;
}
</style>
