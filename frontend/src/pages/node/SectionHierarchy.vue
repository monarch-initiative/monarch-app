<template>
  <div class="toc-hier" role="group" aria-label="Hierarchy preview">
    <div class="toc-hier-title">{{ title }}</div>
    <!-- PARENTS (multi) -->
    <div class="parents">
      <div class="parent-row" v-for="p in parents" :key="p.id">
        <span class="bar" aria-hidden="true"></span>
        <RouterLink :to="`/${p.id}`" :title="labelOf(p)" class="row-text">
          {{ labelOf(p) }}
        </RouterLink>
      </div>
    </div>

    <!-- CURRENT NODE -->
    <div class="current-row">
      <span class="bar" aria-hidden="true"></span>
      <strong class="row-text" :title="labelOf(node)">{{
        labelOf(node)
      }}</strong>
    </div>

    <!-- CHILDREN -->
    <div class="children">
      <div class="child-row" v-for="c in shownChildren" :key="c.id">
        <span class="bar" aria-hidden="true"></span>
        <span class="connector" aria-hidden="true"></span>
        <!-- NEW -->
        <RouterLink :to="`/${c.id}`" class="row-text" :title="labelOf(c)">
          {{ labelOf(c) }}
        </RouterLink>
      </div>

      <RouterLink
        v-if="moreCount > 0"
        :to="'#Hierarchy'"
        class="more"
        title="Show full list in the Hierarchy section"
      >
        + {{ moreCount }} more…
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Node } from "@/api/model";

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

function labelOf(n: any): string {
  return n?.name ?? n?.label ?? n?.id ?? "";
}
</script>

<style lang="scss" scoped>
/* Fully aligned hierarchy styles: bar | connector | text
   - spine is row-scoped (per .child-row)
   - tick is attached to the child text (::before), so it aligns with the first line
*/
.toc-hier {
  /* perceived indents (bar widths) */
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

  --row-gap-parent: 4px; /* spacing between parent rows */
  --row-gap-current: 6px; /* spacing above/below current row */
  --row-gap-child: 6px; /* spacing between child rows */

  margin: 2em 1.5em 3em 1.5em;
  padding-bottom: var(--bottom-gap);
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
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
  font-size: 0.9em;
}

/* ===== Parents (bar | text) ===== */
.parent-row {
  display: grid;
  position: relative;
  grid-template-columns: var(--parent-bar) 1fr;
  column-gap: var(--gap);
  align-items: center;
  margin: 4px 0;
}
.parent-row .bar {
  box-sizing: content-box;
  justify-self: end;
  width: var(--parent-bar);
  height: var(--bar-h);
  background: #e5e7eb;
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
/* ===== Current (bar | text) + spine stub ===== */
.current-row {
  display: grid;
  position: relative;
  grid-template-columns: var(--current-bar) 1fr;
  column-gap: var(--gap);
  align-items: center;
  margin: 4px 0;
}
.current-row .bar {
  box-sizing: content-box;
  justify-self: end;
  width: var(--current-bar);
  height: var(--bar-h);
  background: #e5e7eb;
}
/* spine at end of current bar */
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

/* ===== Children (bar | connector | text) ===== */
.children {
  margin: 4px 0;
}

.child-row {
  display: grid;
  position: relative;
  grid-template-columns: var(--child-bar) var(--connector-w) 1fr; /* bar | connector | text */
  column-gap: 0.3em; /* connector encodes spacing */

  align-items: center;
  margin: 4px 0;
}

/* child bar ends flush with connector */
.child-row .bar {
  box-sizing: content-box;
  top: var(--child-bar-offset-y);
  justify-self: end;
  width: var(--child-bar);
  height: var(--bar-h);
  background: #e5e7eb;
}

.connector {
  position: relative;
  height: 1.2em; /* enough to cover the first line */
}

.connector::before {
  position: absolute;
  top: -2px;
  bottom: -2px;
  left: 0;
  width: var(--spine-w);
  background: #111827;
  content: ""; /* vertical spine */
}
.connector::after {
  position: absolute;
  top: var(--tick-top);
  left: var(--spine-w);
  width: var(--hyphen-w);
  height: 1px;
  background: #111827;
  content: ""; /* horizontal tick */
}

/* child text sits in column 3 */
.child-row .row-text {
  display: block;
  grid-column: 3;
  min-width: 0;
  max-width: 100%;
  overflow: hidden; /* key for ellipsis */
  text-overflow: ellipsis;
  white-space: nowrap;
  /* color: #2563eb;  // if you’re not using $theme */
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

.parent-row {
  margin-block: var(--row-gap-parent);
}
.current-row {
  margin-block: var(--row-gap-current);
}
.child-row {
  margin-block: var(--row-gap-child);
}
.connector {
  height: calc(1.2em + var(--row-gap-child));
}
</style>
