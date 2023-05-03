<template>
  <AppFlex
    ref="toc"
    flow="inline"
    direction="col"
    gap="none"
    h-align="stretch"
    class="toc"
    :style="{ top: nudge + 'px' }"
    :data-expanded="expanded"
    role="doc-toc"
    aria-label="Page table of contents"
    @click.stop
  >
    <!-- toggle button -->
    <div class="title">
      <button
        v-tooltip="
          expanded ? 'Close table of contents' : 'Expand table of contents'
        "
        class="title-button"
        :aria-expanded="expanded"
        @click="expanded = !expanded"
      >
        <AppIcon :icon="expanded ? 'times' : 'bars'" />
      </button>
      <span v-if="expanded" class="title-text truncate">Table of Contents</span>
    </div>

    <template v-if="expanded">
      <div class="spacer"></div>

      <!-- entries -->
      <AppLink
        v-for="(entry, index) in entries"
        :key="index"
        :to="'#' + entry.id"
        class="entry"
        :data-active="active === index"
        :aria-current="active === index"
        @click="active = index"
      >
        <AppIcon :icon="entry.icon" class="entry-icon" />
        <span class="entry-text truncate">{{ entry.text }}</span>
      </AppLink>

      <div class="spacer"></div>

      <!-- options -->
      <AppCheckbox
        v-model="oneAtATime"
        v-tooltip="'Only show one section at a time'"
        text="Show single section"
      />
    </template>
  </AppFlex>
</template>

<script lang="ts">
/** Close the table of contents panel */
export const closeToc = (): unknown =>
  window.dispatchEvent(new CustomEvent("closetoc"));
</script>

<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import {
  onClickOutside,
  useEventListener,
  useMutationObserver,
} from "@vueuse/core";
import { firstInView } from "@/util/dom";
import AppCheckbox from "./AppCheckbox.vue";

type Entries = {
  section: HTMLElement;
  id: string;
  icon: string;
  text: string;
}[];

/** Toc entries */
const entries = ref<Entries>([]);
/** Whether toc is open or not */
const expanded = ref(window.innerWidth > 1400);
/** How much to push downward to make room for header if in view */
const nudge = ref(0);
/** Whether to only show one section at a time */
const oneAtATime = ref(false);
/** Active (in view or selected) section */
const active = ref(0);

/** Table of contents panel element */
const toc = ref<HTMLElement>();

/** Listen for close event */
useEventListener(window, "closetoc", () => (expanded.value = false));

/** Update toc position */
async function updatePosition() {
  /** Wait for rendering to finish */
  await nextTick();

  /** Get dimensions of header and "sub-header" (e.g. first section on node page) */
  const headerEl = document?.querySelector("header");
  const subHeaderEl = document?.querySelector("main > section:first-child");
  if (!headerEl || !subHeaderEl) return;
  const header = headerEl.getBoundingClientRect();
  const subHeader = subHeaderEl.getBoundingClientRect();

  /** Calculate nudge */
  nudge.value = Math.max(
    header.top + header.height,
    subHeader.top + subHeader.height
  );

  /** Find in view section */
  if (!oneAtATime.value)
    active.value = firstInView(
      /** typescript bug */
      entries.value.map((entry) => entry.section as HTMLElement)
    );
}

/** Update toc entries */
function updateEntries() {
  entries.value = Array.from(
    /** Get all headings except top level one */
    document?.querySelectorAll("h2[id], h3[id]") || []
  ).map((element) =>
    /** Get relevant props from heading */
    ({
      section: (element.closest("section") as HTMLElement) || null,
      id: element.getAttribute("id") || "",
      icon:
        element.querySelector("[data-icon]")?.getAttribute("data-icon") || "",
      text: (element as HTMLElement).innerText || "",
    })
  );
}

/** Hide/show sections based on active */
function hideShow() {
  for (const [index, { section }] of Object.entries(entries.value))
    if (section)
      section.style.display =
        active.value === Number(index) || !oneAtATime.value ? "" : "none";
}

/** When user clicks "off" of toc panel */
onClickOutside(toc, () => {
  if (expanded.value && window.innerWidth < 1240) expanded.value = false;
});

watch(oneAtATime, hideShow);

watch(active, hideShow);

/** Run update on: page load, scroll, resize, reflow, etc. */
onMounted(updateEntries);
onMounted(updatePosition);
useEventListener(window, "scroll", updatePosition);
useEventListener(window, "resize", updatePosition);
useMutationObserver(
  document?.body,
  () => {
    updatePosition();
    updateEntries();
  },
  {
    subtree: true,
    childList: true,
  }
);
</script>

<style lang="scss" scoped>
.toc {
  position: fixed;
  top: 0;
  background: $white;
  box-shadow: $shadow;
  z-index: 10;
}

.toc[data-expanded="true"] {
  width: 210px;
  max-width: calc(100vw - 40px);
}

.title {
  display: flex;
  align-items: center;
}

.title-button {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.title-text {
  padding-right: 20px;
  font-weight: 500;
}

.spacer {
  content: "";
  width: 100%;
  margin: 5px 0;
}

.entry {
  display: flex;
  align-items: center;
  height: 40px;
  text-decoration: none;
  transition: background $fast;
}

.entry[data-active="true"] {
  background: $light-gray;
}

.entry:hover {
  background: $light-gray;
}

.entry-icon {
  width: 40px;
  flex-shrink: 0;
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
</style>
