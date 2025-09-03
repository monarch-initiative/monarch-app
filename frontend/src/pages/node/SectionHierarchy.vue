<template>
  <div class="toc-hier" role="group" aria-label="Hierarchy preview">
    <div class="toc-hier-title">{{ title }}</div>

    <!-- PARENTS -->
    <div class="parents">
      <div class="parent-row" v-for="p in parents" :key="p.id">
        <RouterLink :to="`/${p.id}`" :title="labelOf(p)" class="row-text">
          {{ labelOf(p) }}
        </RouterLink>
      </div>
    </div>

    <!-- CURRENT NODE -->
    <div class="current-row">
      <strong class="row-text" :title="labelOf(node)">{{
        labelOf(node)
      }}</strong>
    </div>

    <!-- CHILDREN (tree connectors only) -->
    <div class="children">
      <div class="child-row" v-for="c in shownChildren" :key="c.id">
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

const labelOf = (n: any): string => n?.name ?? n?.label ?? n?.id ?? "";

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
/* Minimal styles to keep tree layout (no bars) */
.toc-hier {
  --indent-parent: 2em;
  --indent-current: 3em;
  --indent-child: 4em;
  --spine-w: 1px;
  --tick-w: 8px;
  --gap: 4px;
  --tick-top: 0.7em;
  margin: 1em;
  border-bottom: 1px solid $light-gray;
  font-size: 14px;
  line-height: 1.5;
}

.toc-hier-title {
  margin-bottom: 0.7em;
  font-weight: 500;
}
.parent-row,
.current-row,
.child-row {
  margin: 4px 0;
}
.parent-row {
  padding-left: var(--indent-parent);
}
.current-row {
  position: relative;
  padding-left: calc(var(--indent-current) + var(--tick-w) + var(--gap));
}
/* current-node spine + tick */
.current-row::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: var(--indent-current);
  width: var(--spine-w);
  background: #111827;
  content: "";
}
.current-row::after {
  position: absolute;
  top: var(--tick-top);
  left: var(--indent-current);
  width: var(--tick-w);
  height: 1px;
  background: #111827;
  content: "";
}

/* Children show a vertical spine + a small tick before each label */
.child-row {
  position: relative;
  padding-left: calc(var(--indent-child) + var(--tick-w) + var(--gap));
}
.child-row::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: var(--indent-child);
  width: var(--spine-w);
  background: #111827;
  content: "";
}
.child-row::after {
  position: absolute;
  top: var(--tick-top);
  left: var(--indent-child);
  width: var(--tick-w);
  height: 1px;
  background: #111827;
  content: "";
}

.row-text {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-decoration: none;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row-text:hover {
  text-decoration: underline;
}

.more {
  display: inline-block;
  margin-top: 0.5em;
  margin-left: calc(var(--indent-child) + var(--tick-w) + var(--gap));
  border: 0;
  background: none;
  color: #6b7280;
  cursor: pointer;
}

.modal-title {
  font-weight: 600;
  font-size: 1rem;
}
.hier-modal-list {
  margin: 0;
  padding: 6px 0;
}
.hier-modal-list li {
  list-style: circle; /* optional: per-item override */
}
</style>
