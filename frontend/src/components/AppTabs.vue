<!--
  tab buttons that conditionally show their corresponding slots

  references:
  https://www.w3.org/TR/2021/NOTE-wai-aria-practices-1.2-20211129/examples/tabs/tabs-1/tabs.html
-->

<template>
  <AppFlex role="tablist" :aria-label="name">
    <AppButton
      v-for="(tab, index) in tabs"
      :id="`tab-${id}-${tab.id}`"
      :key="index"
      v-tooltip="tab.tooltip"
      :text="tab.text"
      :icon="tab.icon"
      design="circle"
      :color="modelValue === tab.id ? 'primary' : 'none'"
      :aria-label="tab.text"
      :aria-selected="modelValue === tab.id"
      :aria-controls="`panel-${id}-${tab.id}`"
      :tabindex="modelValue === tab.id ? 0 : undefined"
      role="tab"
      @click="onClick(tab.id)"
      @keydown="onKeydown"
    />
  </AppFlex>

  <!-- hidden element to serve as aria panel -->
  <div
    :id="`panel-${id}-${modelValue}`"
    :aria-labelledby="`tab-${id}-${modelValue}`"
    role="tabpanel"
    :aria-label="'Tab content below'"
    :style="{ display: 'contents' }"
  ></div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { uniqueId } from "lodash";
import { wrap } from "@/util/math";

/** route info */
const router = useRouter();
const route = useRoute();

type Tab = {
  /** page-wide unique id of tab */
  id: string;
  /** tab button props */
  text?: string;
  icon?: string;
  description?: string;
  tooltip?: string;
};
type Tabs = Tab[];

type Props = {
  /** two-way bound selected tab state */
  modelValue: string;
  /** list of tabs with info */
  tabs: Tabs;
  /** name of tab group */
  name: string;
  /** whether to sync active tab with url hash */
  url?: boolean;
  /** route name to navigate to on change */
  navigate?: string;
};

const props = withDefaults(defineProps<Props>(), {
  url: true,
  navigate: undefined,
});

type Emits = {
  /** two-way bound selected tab state */
  "update:modelValue": [string];
};

const emit = defineEmits<Emits>();

/** unique id for instance of component */
const id = ref(uniqueId());

/** when user clicks on button */
async function onClick(id: string) {
  emit("update:modelValue", id);
}

/** when user presses key on button */
async function onKeydown(event: KeyboardEvent) {
  if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
    /** prevent page scroll */
    event.preventDefault();

    /** move selected tab */
    let index = props.tabs.findIndex((tab) => tab.id === props.modelValue);
    if (event.key === "ArrowLeft") index--;
    if (event.key === "ArrowRight") index++;
    if (event.key === "Home") index = 0;
    if (event.key === "End") index = props.tabs.length - 1;

    /** update selected, wrapping beyond -1 or options length */
    emit(
      "update:modelValue",
      props.tabs[wrap(index, 0, props.tabs.length - 1)].id,
    );
  }
}

/** get appropriate tab from url hash */
function getHash() {
  /** set selected tab to id in hash */
  const hash = route?.hash?.slice(1) || "";
  /** if there is a tab with name equal to hash, return that one */
  if (props.tabs.find((tab) => tab.id === hash)) return hash;
  else return "";
}

/** when selected tab changes */
watch(
  () => props.modelValue,
  async () => {
    /** focus the selected tab */
    // const selector = `#tab-${id.value}-${props.modelValue}`;
    // const button = document?.querySelector<HTMLButtonElement>(selector);
    // button?.focus();

    /** update hash in url and nav if applicable */
    const newRoute = { ...route };
    if (props.navigate) newRoute.name = props.navigate;
    if (props.url) newRoute.hash = "#" + props.modelValue;
    await router.push(newRoute);
  },
);

/** update state */
function updateState() {
  if (props.url && getHash()) emit("update:modelValue", getHash());
}

onMounted(updateState);
watch(() => route.hash, updateState);
</script>
