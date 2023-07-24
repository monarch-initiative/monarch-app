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
      <span class="box-label">{{ modelValue?.label || modelValue?.id }}</span>
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
            {{ option.label || option.id }}
          </span>
          <span v-if="option.count" class="option-count">
            {{ option.count }}
          </span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script lang="ts">
export type Option = {
  /** unique id used in state of select */
  id: string;
  /** icon name */
  icon?: string;
  /** display label */
  label?: string;
  /** count col */
  count?: number;
  /** tooltip on hover */
  tooltip?: string;
};

export type Options = Option[];
</script>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import { uniqueId } from "lodash";
import { useFloating } from "@/util/composables";
import { wrap } from "@/util/math";

type Props = {
  /** two-way bound selected item state */
  modelValue?: Option;
  /** name of the field */
  name: string;
  /** list of options to show */
  options: Options;
};

const props = defineProps<Props>();

type Emits = {
  /** two-way bound selected item state */
  (event: "update:modelValue", value: Option): void;
};

const emit = defineEmits<Emits>();

/** unique id for instance of component */
const id = ref(uniqueId());
/** whether dropdown is open */
const expanded = ref(false);
/** index of option that is selected */
const selected = ref(getSelected());
/** index of option that is highlighted */
const highlighted = ref(0);

/** target element */
const target = ref();
/** dropdown element */
const dropdown = ref();
/** get dropdown position */
const { calculate, style } = useFloating(target, dropdown);
/** recompute position after opened */
watch(expanded, async () => {
  await nextTick();
  if (expanded.value) calculate();
});

/** open dropdown */
function open() {
  expanded.value = true;
  /** auto highlight selected option */
  highlighted.value = selected.value;
}

/** close dropdown */
function close() {
  expanded.value = false;
}

/** when button clicked */
function onClick() {
  /** toggle dropdown */
  expanded.value ? close() : open();
  /** https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#clicking_and_focus */
  (document.querySelector(`#select-${id.value}`) as HTMLElement)?.focus();
}

/** when button blurred */
function onBlur() {
  close();
}

/** when user presses key on button */
function onKeydown(event: KeyboardEvent) {
  /** arrow/home/end keys */
  if (["ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) {
    /** prevent page scroll */
    event.preventDefault();

    /**
     * if dropdown open, control highlighted option. if dropdown closed, control
     * selected option.
     */
    let index = expanded.value ? highlighted.value : selected.value;

    /** move value up/down */
    if (event.key === "ArrowUp") index--;
    if (event.key === "ArrowDown") index++;
    if (event.key === "Home") index = 0;
    if (event.key === "End") index = props.options.length - 1;

    /** update value, wrapping beyond 0 or options length */
    index = wrap(index, 0, props.options.length - 1);
    if (expanded.value) highlighted.value = index;
    else selected.value = index;
  }

  /** enter key to select highlighted option */
  if (expanded.value && (event.key === "Enter" || event.key === " ")) {
    /** prevent browser re-clicking open button */
    event.preventDefault();
    selected.value = highlighted.value;
  }

  /** esc key to close dropdown */
  if (expanded.value && event.key === "Escape") close();
}

/** get selected option index from model */
function getSelected() {
  return props.options.findIndex(
    (option) => option?.id === props.modelValue?.id
  );
}

/** when model changes */
watch(
  () => props.modelValue,
  () =>
    /** update selected index */
    (selected.value = getSelected())
);

/** when selected index changes */
watch(selected, () => {
  /** emit updated model */
  emit("update:modelValue", props.options[selected.value]);
  close();
});

/** when highlighted index changes */
watch(highlighted, () =>
  /** scroll to highlighted in dropdown */
  document
    .querySelector(`#option-${id.value}-${highlighted.value}`)
    ?.scrollIntoView({ block: "nearest" })
);

/** auto-select first option as fallback */
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
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 5px 10px;
  gap: 10px;
  border-radius: $rounded;
  background: $light-gray;
}

.box-label {
  flex-grow: 1;
  text-align: left;
}

.list {
  z-index: 12;
  position: fixed;
  max-width: 90vw;
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
