<!--
  small info affordance that explains a predicate: its definition plus a
  parents/current/children slice of the biolink predicate hierarchy, loaded on
  demand from the biolink model
-->

<template>
  <span class="predicate-info">
    <AppButton
      v-tooltip="'What does this relationship mean?'"
      class="info-button"
      design="small"
      icon="circle-info"
      :aria-label="`Explain ${formatted}`"
      @click.stop.prevent="onOpen"
    />

    <AppModal v-model="show" :label="`Relationship: ${formatted}`">
      <div class="explainer">
        <h2 class="name">{{ formatted }}</h2>

        <AppStatus v-if="isLoading" code="loading">
          Loading definition
        </AppStatus>

        <template v-else-if="info">
          <p class="definition">
            {{ info.description || "No description available." }}
          </p>

          <div v-if="graphRows.length > 1" class="section">
            <h3>Biolink Model Predicate Hierarchy</h3>
            <div class="hier-graph">
              <div
                v-for="row in graphRows"
                :key="row.kind + row.name"
                class="hier-row"
                :class="row.kind"
                :style="{ '--depth': row.depth }"
              >
                <span v-if="row.kind === 'current'" class="hier-label">{{
                  format(row.name)
                }}</span>
                <AppLink v-else class="hier-label" :to="docsFor(row.name)">{{
                  format(row.name)
                }}</AppLink>
              </div>
              <button
                v-if="moreChildren > 0"
                type="button"
                class="hier-more"
                :style="{ '--depth': childDepth }"
                @click="showAllChildren = true"
              >
                + {{ moreChildren }} more
              </button>
            </div>
          </div>

          <dl v-if="info.inverse" class="section meta">
            <dt>Inverse</dt>
            <dd>{{ format(info.inverse) }}</dd>
          </dl>

          <p class="attribution">
            Definition from the
            <AppLink :to="docsFor(predicate)">Biolink Model</AppLink>.
          </p>
        </template>

        <AppStatus v-else code="warning">
          No definition found for this relationship in the biolink model.
        </AppStatus>
      </div>
    </AppModal>
  </span>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppModal from "@/components/AppModal.vue";
import AppStatus from "@/components/AppStatus.vue";
import {
  useBiolinkModel,
  type PredicateInfo,
} from "@/composables/use-biolink-model";

type Props = {
  /** predicate curie/name, e.g. "biolink:treats" */
  predicate: string;
};

const props = defineProps<Props>();

const {
  isLoading,
  loadBiolinkModel,
  getPredicateInfo,
  getPredicateAncestors,
  getPredicateChildren,
} = useBiolinkModel();

const show = ref(false);
const info = ref<PredicateInfo | null>(null);
const ancestors = ref<PredicateInfo[]>([]);
const children = ref<PredicateInfo[]>([]);
const showAllChildren = ref(false);

const CHILD_LIMIT = 12;

/** human-readable predicate label */
const format = (value?: string): string =>
  (value ?? "").replace(/^biolink:/, "").replace(/_/g, " ");

/** link to a predicate's page in the biolink model docs */
const docsFor = (name: string): string =>
  `https://biolink.github.io/biolink-model/${name
    .replace(/^biolink:/, "")
    .replace(/ /g, "_")}/`;

const formatted = computed(() => format(props.predicate));

const childDepth = computed(() => ancestors.value.length + 1);
const shownChildren = computed(() =>
  showAllChildren.value ? children.value : children.value.slice(0, CHILD_LIMIT),
);
const moreChildren = computed(
  () => children.value.length - shownChildren.value.length,
);

type Row = {
  name: string;
  kind: "ancestor" | "current" | "child";
  depth: number;
};

/** parents (general → specific), the current predicate, then its children */
const graphRows = computed<Row[]>(() => {
  const rows: Row[] = [];
  [...ancestors.value].reverse().forEach((a, index) => {
    rows.push({ name: a.name, kind: "ancestor", depth: index });
  });
  rows.push({
    name: props.predicate,
    kind: "current",
    depth: ancestors.value.length,
  });
  shownChildren.value.forEach((child) => {
    rows.push({ name: child.name, kind: "child", depth: childDepth.value });
  });
  return rows;
});

/** load the definition + hierarchy lazily when the modal is opened */
async function onOpen() {
  show.value = true;
  if (info.value) return;
  await loadBiolinkModel();
  info.value = getPredicateInfo(props.predicate);
  ancestors.value = getPredicateAncestors(props.predicate);
  children.value = getPredicateChildren(props.predicate);
}
</script>

<style lang="scss" scoped>
.info-button {
  color: $gray;
  opacity: 0.6;
}
.info-button:hover {
  opacity: 1;
}

.explainer {
  max-width: 500px;
}

.name {
  font-size: 1.1rem;
}

.definition {
  margin: 0.5em 0 1em;
}

.section {
  margin-top: 1em;
}

.section h3 {
  margin-bottom: 0.4em;
  color: $gray;
  font-size: 0.9rem;
}

/* parents/current/children tree */
.hier-graph {
  margin-top: 0.2em;
}
.hier-row {
  position: relative;
  margin-left: calc(var(--depth) * 1.2em);
  padding: 3px 0 3px 1em;
  border-left: 2px solid $light-gray;
}
.hier-row::before {
  position: absolute;
  top: 0.85em;
  left: 0;
  width: 0.7em;
  height: 2px;
  background: $light-gray;
  content: "";
}
.hier-row.current {
  border-left-color: $off-black;
  font-weight: 600;
}
.hier-row.current::before {
  background: $off-black;
}
.hier-more {
  margin-left: calc(var(--depth) * 1.2em + 1em);
  padding: 3px 0;
  border: 0;
  background: none;
  color: $gray;
  font-size: 0.85em;
  cursor: pointer;
}
.hier-more:hover {
  text-decoration: underline;
}

.meta {
  display: grid;
  grid-template-columns: auto 1fr;
  margin: 0;
  gap: 2px 1em;
}
.meta dt {
  color: $gray;
}
.meta dd {
  margin: 0;
}

.attribution {
  margin: 1.5em 0 0;
  color: $gray;
  font-size: 0.85em;
}
</style>
