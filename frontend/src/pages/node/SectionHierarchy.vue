<template>
  <div class="toc-hier" role="group" aria-label="Hierarchy preview">
    <div class="toc-hier-title">{{ title }}</div>

    <!-- PARENTS (keep spacing, hide bars) -->
    <div class="parents">
      <div class="parent-row" v-for="p in parents" :key="p.id">
        <span class="bar" aria-hidden="true"></span>
        <RouterLink :to="`/${p.id}`" :title="labelOf(p)" class="row-text">
          {{ labelOf(p) }}
        </RouterLink>
      </div>
    </div>

    <!-- CURRENT NODE (keep spacing + spine, hide bar) -->
    <div class="current-row">
      <span class="bar" aria-hidden="true"></span>
      <strong class="row-text" :title="labelOf(node)">{{
        labelOf(node)
      }}</strong>
    </div>

    <!-- CHILDREN (keep connector + spacing, hide child bars) -->
    <div class="children">
      <div class="child-row" v-for="c in shownChildren" :key="c.id">
        <span class="bar" aria-hidden="true"></span>
        <span class="connector" aria-hidden="true"></span>
        <RouterLink :to="`/${c.id}`" class="row-text" :title="labelOf(c)">
          {{ labelOf(c) }}
        </RouterLink>
      </div>

      <button
        v-if="moreCount > 0"
        type="button"
        class="more"
        @click="openModal"
        title="Show full list"
      >
        + {{ moreCount }} more…
      </button>

      <AppModal v-model="showAll" :label="modalTitle">
        <h2 class="modal-title">{{ modalTitle }}</h2>

        <ul class="hier-modal-list">
          <li v-for="c in remainingChildren" :key="c.id">
            <RouterLink :to="`/${c.id}`" @click="closeModal">
              {{ labelOf(c) }}
            </RouterLink>
          </li>
        </ul>
      </AppModal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { Node } from "@/api/model";
import AppModal from "@/components/AppModal.vue";

const props = defineProps<{ node: Node; childLimit?: number }>();

const LABELS = new Map<string, string>([
  ["biolink:Disease", "Disease"],
  ["biolink:PhenotypicFeature", "Phenotype"],
  ["biolink:AnatomicalEntity", "Anatomical entity"],
]);

const typeNoun = computed(
  () => LABELS.get(props.node?.category ?? "") ?? "Hierarchy",
);
const title = computed(() => `${typeNoun.value} hierarchy`);

const parents = computed<any[]>(
  () => props.node.node_hierarchy?.super_classes ?? [],
);
const children = computed<any[]>(
  () => props.node.node_hierarchy?.sub_classes ?? [],
);

const limit = computed(() => props.childLimit ?? 6);
const shownChildren = computed(() => children.value.slice(0, limit.value));
const moreCount = computed(() =>
  Math.max(0, children.value.length - shownChildren.value.length),
);

const labelOf = (n: any): string => {
  return n?.name ?? n?.label ?? n?.id ?? "";
};

const showAll = ref(false);
const remainingChildren = computed(() => children.value.slice(limit.value));
const openModal = () => (showAll.value = true);
const closeModal = () => (showAll.value = false);

// Modal
const nodeName = computed(() => labelOf(props.node));
const totalChildren = computed(() => children.value.length);
const modalTitle = computed(
  () =>
    `${totalChildren.value === 1 ? "Subclass" : "Subclasses"} of ${nodeName.value}`,
);
</script>

<style lang="scss" scoped>
.toc-hier {
  /* perceived indents (bar widths retained for spacing) */
  --bar-h: 6px;
  --parent-bar: 2em;
  --current-bar: 3em;
  --child-bar: 4em;

  /* spacing */
  --bar-gap: 4px; /* gap between any bar end and the spine */
  --spine-w: 1px; /* vertical line width */
  --hyphen-w: 8px; /* child tick length */
  --child-gap: 6px; /* space after tick before text */
  /* connector column = spine + tick + gap to text */
  --connector-w: calc(var(--spine-w) + var(--hyphen-w) + var(--child-gap));
  /* single source of truth for spine X positions */
  --current-spine-x: calc(var(--current-bar) + var(--bar-gap));
  --child-spine-x: calc(var(--child-bar) + var(--bar-gap));
  /* tick baseline alignment (relative to first line of text) */
  --tick-top: 0.7em;
  /* general spacing */
  --gap: 6px;
  --bottom-gap: 1.5em;

  --row-gap-child: 6px; /* spacing between child rows */

  margin: 2em 1.5em 3em 1.5em;
  padding-bottom: var(--bottom-gap);
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.9em;
  line-height: 1.5;
  .more {
    margin-top: 2px;
  }
}

.toc-hier-title {
  display: flex;
  padding-bottom: 0.9em;
  color: $off-black;
  font-weight: 500;
  font-size: 1em;
}

/* ===== Parents (placeholder column | text) ===== */
.parent-row {
  display: grid;
  position: relative;
  grid-template-columns: var(--parent-bar) 1fr; /* keep indent */
  column-gap: var(--gap);
  align-items: center;
  margin: 4px 0;
}

.parent-row .row-text,
.current-row .row-text {
  display: block;
  grid-column: 2;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== Current (placeholder column | text) + spine stub ===== */
.current-row {
  display: grid;
  position: relative;
  grid-template-columns: var(--current-bar) 1fr; /* keep indent */
  column-gap: var(--gap);
  align-items: center;
  margin: 4px 0;
}

/* spine at end of current indent (same as before) */
.current-row::after {
  z-index: 1;
  position: absolute;
  top: -0.25em;
  bottom: -0.15em;
  left: var(--current-spine-x);
  width: var(--spine-w);
  background: #111827;
  content: "";
}

/* ===== Children (placeholder column | connector | text) ===== */

.child-row {
  display: grid;
  position: relative;
  grid-template-columns: var(--child-bar) var(--connector-w) 1fr; /* keep indent */
  align-items: center;
  margin: 4px 0;
}

.connector {
  position: relative;
  height: 1.2em;
}

.connector::before {
  position: absolute;
  top: -2px;
  bottom: -2px;
  left: 0;
  width: var(--spine-w);
  background: #111827;
  content: "";
}
.connector::after {
  position: absolute;
  top: var(--tick-top);
  left: var(--spine-w);
  width: var(--hyphen-w);
  height: 1px;
  background: #111827;
  content: "";
}

/* child text sits in column 3 */
.child-row .row-text {
  display: block;
  grid-column: 3;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Links */
.row-text {
  text-decoration: none;
}
.row-text:hover {
  text-decoration: underline;
}

/* “+ more…” aligned with the child text column */
.more {
  display: inline-block;
  margin-left: calc(
    var(--child-bar) + var(--bar-gap) + var(--spine-w) + var(--hyphen-w) +
      var(--child-gap)
  );
  color: #6b7280;
  text-decoration: none;
}
.more:hover {
  text-decoration: underline;
}

.connector {
  height: calc(1.2em + var(--row-gap-child));
}

.modal-title {
  font-weight: 600;
  font-size: 1rem;
  text-align: center;
}
.hier-modal-list {
  inline-size: fit-content;
  font-size: 01em;
  list-style: circle;
}

/* comfy items + subtle hover */
.hier-modal-list li {
  padding: 1px 12px;
  border-radius: 10px;
  color: $theme;
  transition:
    background 150ms ease,
    transform 150ms ease;
}

.hier-modal-list a {
  display: block;
  color: inherit;

  text-decoration: none;
  overflow-wrap: anywhere;
}

.hier-modal-list li:hover,
.hier-modal-list a:focus-visible {
  transform: translateX(2px);
  background: #f3f4f6; /* soft highlight */
}
</style>
