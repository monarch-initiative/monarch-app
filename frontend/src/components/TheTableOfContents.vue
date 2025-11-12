<template>
  <aside aria-label="table of contents">
    <AppFlex
      ref="toc"
      flow="inline"
      direction="col"
      gap="none"
      align-h="stretch"
      align-v="top"
      :class="['toc', { expanded }]"
      :style="{ top: nudge + 'px' }"
      role="doc-toc"
      aria-label="Page table of contents"
      @click.stop
    >
      <AppBackToTopButton />

      <SectionHierarchy
        v-if="node && showHierarchy"
        :node="node"
        :child-limit="10"
      />

      <!-- entries -->
      <AppLink
        v-for="(entry, index) in entries"
        :key="index"
        :to="'#' + entry.id"
        :replace="true"
        :class="['entry', { active: active === index }]"
        :aria-current="active === index"
        @click="active = index"
      >
        <AppIcon :icon="entry.icon" class="entry-icon" />
        <span class="entry-text truncate">{{ entry.text }}</span>
      </AppLink>

      <div class="spacer"></div>

      <!-- options -->
      <!-- <AppCheckbox
        v-model="oneAtATime"
        v-tooltip="'Only show one section at a time'"
        text="Show single section"
      /> -->
    </AppFlex>
  </aside>
</template>

<script lang="ts">
/** close the table of contents panel */
export const closeToc = (): unknown =>
  window.dispatchEvent(new CustomEvent("closetoc"));
</script>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import {
  onClickOutside,
  useEventListener,
  useMutationObserver,
} from "@vueuse/core";
import type { Node as ApiNode } from "@/api/model";
import AppBackToTopButton from "@/components/AppBackToTopButton.vue";
import SectionHierarchy from "@/pages/node/SectionHierarchy.vue";
import { firstInView } from "@/util/dom";
import type AppFlex from "./AppFlex.vue";

type Entries = {
  section: HTMLElement | null;
  id: string;
  icon: string;
  text: string;
}[];

const CATEGORIES = [
  "biolink:Disease",
  "biolink:PhenotypicFeature",
  "biolink:AnatomicalEntity",
];
const { node } = defineProps<{ node: ApiNode | null }>();
/** toc entries */
const entries = ref<Entries>([]);
/** whether toc is open or not */
const expanded = ref(window.innerWidth > 1240);
/** how much to push downward to make room for header if in view */
const nudge = ref(0);
/** whether to only show one section at a time */
const oneAtATime = ref(false);
/** active (in view or selected) section */
const active = ref(0);
const showHierarchy = computed(() => CATEGORIES.includes(node?.category ?? ""));
/** table of contents panel element */
const toc = ref<InstanceType<typeof AppFlex>>();
/** listen for close event */
useEventListener(window, "closetoc", () => (expanded.value = false));
/** toggle expanded state */
useEventListener(window, "resize", () => {
  if (window.innerWidth < 1240) {
    // on narrow, always collapse
    expanded.value = false;
  } else {
    // on wide, always expand
    expanded.value = true;
  }
});

/** update toc position */
async function updatePosition() {
  /** wait for rendering to finish */
  await nextTick();

  /** get dimensions of header and "sub-header" (e.g. first section on node page) */
  const headerEl = document.querySelector("header");
  const subHeaderEl = document.querySelector("main > section:first-child");
  if (!headerEl || !subHeaderEl) return;
  const header = headerEl.getBoundingClientRect();

  /** calculate nudge */
  nudge.value = Math.max(header.top + header.height);

  /** find in view section */
  if (!oneAtATime.value)
    active.value = firstInView(
      /** typescript bug */
      entries.value
        .map((entry) => entry.section)
        .filter(Boolean) as HTMLElement[],
    );
}

/** update toc entries */
function updateEntries() {
  entries.value = Array.from(
    /** get all headings except top level one */
    document.querySelectorAll<HTMLElement>("h2[id], h3[id]") || [],
  ).map((element) =>
    /** get relevant props from heading */
    ({
      section: element.closest<HTMLElement>("section") || null,
      id: element.getAttribute("id") || "",
      icon:
        element.querySelector("[data-icon]")?.getAttribute("data-icon") || "",
      text: element.innerText || "",
    }),
  );
}

/** hide/show sections based on active */
function hideShow() {
  for (const [index, { section }] of Object.entries(entries.value))
    if (section)
      section.style.display =
        active.value === Number(index) || !oneAtATime.value ? "" : "none";
}

/** when user clicks "off" of toc panel */
onClickOutside(toc, () => {
  if (expanded.value && window.innerWidth < 1240) expanded.value = false;
});

watch(oneAtATime, hideShow);

watch(active, hideShow);

/** run update on: page load, scroll, resize, reflow, etc. */
onMounted(updateEntries);
onMounted(updatePosition);
useEventListener(window, "scroll", updatePosition);
useEventListener(window, "resize", updatePosition);
useMutationObserver(
  document.body,
  () => {
    updatePosition();
    updateEntries();
  },
  {
    subtree: true,
    childList: true,
  },
);
</script>

<style lang="scss" scoped>
.toc {
  /* this is an unfortunate hack to get the TOC to be behind the footer */
  z-index: 1009;
  position: fixed;
  top: 0;
  width: $toc-width;
  max-width: calc(100vw - 40px);
  height: 100%;
  background: $white;
  box-shadow: $shadow;
}

.title {
  display: flex;
  align-items: center;
}

.title-button {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
}

.title-text {
  padding-right: 20px;
  font-weight: 500;
}

.spacer {
  width: 100%;
  margin: 5px 0;
  content: "";
}

.entry {
  display: flex;
  align-items: center;
  height: 40px;
  text-decoration: none;
  transition: background $fast;
}

.entry.active {
  background: $light-gray;
}

.entry:hover {
  background: $light-gray;
}

.entry-icon {
  flex-shrink: 0;
  width: 40px;
  color: $gray;
}

.entry-text {
  flex-grow: 1;
  color: $off-black;
  text-align: left;
}

.checkbox {
  font-size: 0.9rem;
}
.toc:not(.expanded) {
  transform: translateX(-100%);
}
</style>
