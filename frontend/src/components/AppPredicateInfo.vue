<!--
  small info affordance that explains a predicate: its definition plus a
  parents/current/children slice of the biolink predicate hierarchy, drawn as an
  indented tree matching the node-page hierarchy, loaded on demand from the
  biolink model
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

          <div v-if="parents.length || children.length" class="section">
            <h3>Biolink Model Predicate Hierarchy</h3>
            <div class="hier" role="group" aria-label="Predicate hierarchy">
              <!-- PARENTS (general -> immediate parent) -->
              <div class="parents">
                <div v-for="p in parents" :key="p.name" class="parent-row">
                  <AppLink
                    v-tooltip="format(p.name)"
                    :to="docsFor(p.name)"
                    class="row-text"
                  >
                    {{ format(p.name) }}
                  </AppLink>
                </div>
              </div>

              <!-- CURRENT PREDICATE -->
              <div class="current-row">
                <strong class="row-text">{{ formatted }}</strong>
              </div>

              <!-- CHILDREN -->
              <div class="children">
                <div v-for="c in shownChildren" :key="c.name" class="child-row">
                  <AppLink
                    v-tooltip="format(c.name)"
                    :to="docsFor(c.name)"
                    class="row-text"
                  >
                    {{ format(c.name) }}
                  </AppLink>
                </div>

                <button
                  v-if="moreCount > 0"
                  type="button"
                  class="more"
                  @click="showAllChildren = true"
                >
                  + {{ moreCount }} more…
                </button>
              </div>
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

const CHILD_LIMIT = 6;

/** human-readable predicate label */
const format = (value?: string): string =>
  (value ?? "").replace(/^biolink:/, "").replace(/_/g, " ");

/** link to a predicate's page in the biolink model docs */
const docsFor = (name: string): string =>
  `https://biolink.github.io/biolink-model/${name
    .replace(/^biolink:/, "")
    .replace(/ /g, "_")}/`;

const formatted = computed(() => format(props.predicate));

/** ancestor chain ordered most-general first, ending just above the current */
const parents = computed(() => [...ancestors.value].reverse());

const shownChildren = computed(() =>
  showAllChildren.value ? children.value : children.value.slice(0, CHILD_LIMIT),
);
const moreCount = computed(
  () => children.value.length - shownChildren.value.length,
);

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

/* indented hierarchy tree, matching the node-page hierarchy preview */
.hier {
  --indent-parent: 1em;
  --indent-current: 2em;
  --indent-child: 3em;
  --spine-w: 1px;
  --tick-w: 8px;
  --gap: 4px;
  --tick-top: 0.7em;
  font-size: 0.9em;
  line-height: 1.5;
}

.parent-row,
.current-row,
.child-row {
  margin: 4px 0;
}
.parent-row {
  padding-left: var(--indent-parent);
}
.current-row,
.child-row {
  position: relative;
}
.current-row {
  padding-left: calc(var(--indent-current) + var(--tick-w) + var(--gap));
}
.child-row {
  padding-left: calc(var(--indent-child) + var(--tick-w) + var(--gap));
}

/* vertical spine + a small tick before the current node and each child */
.current-row::before,
.child-row::before {
  position: absolute;
  top: 0;
  bottom: 0;
  width: var(--spine-w);
  background: $off-black;
  content: "";
}
.current-row::before {
  left: var(--indent-current);
}
.child-row::before {
  left: var(--indent-child);
}

.current-row::after,
.child-row::after {
  position: absolute;
  top: var(--tick-top);
  width: var(--tick-w);
  height: 1px;
  background: $off-black;
  content: "";
}
.current-row::after {
  left: var(--indent-current);
}
.child-row::after {
  left: var(--indent-child);
}

.row-text {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  color: inherit;
  text-decoration: none;
  text-overflow: ellipsis;
  white-space: nowrap;
}
a.row-text:hover {
  text-decoration: underline;
}
.current-row .row-text {
  font-weight: 600;
}

.more {
  display: inline-block;
  margin: 0.5em 0;
  margin-left: calc(var(--indent-child) + var(--tick-w) + var(--gap));
  border: 0;
  background: none;
  color: $gray;
  font-size: 0.95em;
  cursor: pointer;
}
.more:hover {
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
