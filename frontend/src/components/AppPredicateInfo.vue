<!--
  small info affordance that explains a predicate: definition + a partial
  is_a hierarchy, loaded on demand from the biolink model
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

          <div v-if="chain.length > 1" class="section">
            <h3>Hierarchy</h3>
            <ul class="hierarchy">
              <li
                v-for="(item, index) in chain"
                :key="item.name"
                :class="{ current: index === chain.length - 1 }"
                :style="{ paddingLeft: index * 1.25 + 'em' }"
              >
                <AppIcon
                  v-if="index > 0"
                  icon="angle-right"
                  class="branch-icon"
                />
                {{ format(item.name) }}
              </li>
            </ul>
          </div>

          <dl v-if="hasMeta" class="section meta">
            <template v-if="info.domain">
              <dt>Domain</dt>
              <dd>{{ format(info.domain) }}</dd>
            </template>
            <template v-if="info.range">
              <dt>Range</dt>
              <dd>{{ format(info.range) }}</dd>
            </template>
            <template v-if="info.inverse">
              <dt>Inverse</dt>
              <dd>{{ format(info.inverse) }}</dd>
            </template>
          </dl>
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
import AppIcon from "@/components/AppIcon.vue";
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

const { isLoading, loadBiolinkModel, getPredicateInfo, getPredicateAncestors } =
  useBiolinkModel();

const show = ref(false);
const info = ref<PredicateInfo | null>(null);
const ancestors = ref<PredicateInfo[]>([]);

/** human-readable predicate label */
const format = (value?: string): string =>
  (value ?? "").replace(/^biolink:/, "").replace(/_/g, " ");

const formatted = computed(() => format(props.predicate));

/** ancestors (outermost first) followed by the predicate itself */
const chain = computed(() => [
  ...[...ancestors.value].reverse(),
  { name: props.predicate } as PredicateInfo,
]);

const hasMeta = computed(
  () => !!(info.value?.domain || info.value?.range || info.value?.inverse),
);

/** load the definition lazily when the modal is opened */
async function onOpen() {
  show.value = true;
  if (info.value) return;
  await loadBiolinkModel();
  info.value = getPredicateInfo(props.predicate);
  ancestors.value = getPredicateAncestors(props.predicate);
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

.hierarchy {
  margin: 0;
  padding: 0;
  list-style: none;
}
.hierarchy li {
  padding: 2px 0;
}
.hierarchy li.current {
  font-weight: 600;
}
.branch-icon {
  color: $gray;
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
</style>
