<!--
  experimental: dismech disease mechanisms annotated with this node's term (a
  GO process, CL cell type, UBERON location, CHEBI chemical or HGNC gene), and
  the phenotypes each mechanism leads to. self-hides when there are none.
-->

<template>
  <AppSection
    v-if="show && (isLoading || data.rows.length)"
    width="full"
    class="inset"
    alignment="left"
  >
    <AppHeading :level="3">Disease mechanisms involving {{ name }}</AppHeading>
    <AppStatus v-if="isLoading" code="loading">Loading mechanisms</AppStatus>
    <AppStatus v-else-if="isError" code="error"
      >Error loading mechanisms</AppStatus
    >
    <div v-else class="mechanisms">
      <div class="summary">
        <span
          ><strong>{{ data.rows.length.toLocaleString() }}</strong> mechanisms
          in {{ diseases.length.toLocaleString() }} diseases</span
        >
        <span
          ><AppIcon icon="robot" class="ai" /> From Dismech
          <span class="muted"
            >(AI-assisted curation, may have mistakes)</span
          ></span
        >
      </div>
      <table class="rows">
        <thead>
          <tr>
            <th>Disease</th>
            <th>Mechanism</th>
            <th>Leads to</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in visibleRows" :key="row.node_id">
            <td>
              <AppLink v-if="row.mondo_id" :to="`/${row.mondo_id}`">{{
                row.disorder
              }}</AppLink>
              <span v-else>{{ row.disorder }}</span>
            </td>
            <td>
              <span
                v-tooltip="{
                  content: nodeTooltip(data.mechanism_nodes, row.node_id),
                  allowHTML: true,
                  maxWidth: 360,
                  interactive: true,
                  appendTo: appendToBody,
                }"
                class="mechanism"
                >{{ row.node_name }}</span
              >
              <div class="muted">
                {{ row.slots.map(slotLabel).join(", ") }}
                <template v-if="row.modifier">
                  &middot; {{ enumLabel(row.modifier) }}</template
                >
              </div>
            </td>
            <td class="chips">
              <AppLink
                v-for="p in row.leads_to.slice(0, MAX_PHENOTYPES)"
                :key="p.hpo_id"
                :to="`/${p.hpo_id}`"
                :class="['chip', { diagnostic: p.diagnostic }]"
                >{{ p.hpo_label || p.hpo_id }}</AppLink
              >
              <span v-if="row.leads_to.length > MAX_PHENOTYPES" class="muted"
                >+{{ row.leads_to.length - MAX_PHENOTYPES }} more</span
              >
            </td>
          </tr>
        </tbody>
      </table>
      <AppButton
        v-if="data.rows.length > visibleRows.length"
        :text="`Show all ${data.rows.length.toLocaleString()} mechanisms`"
        design="small"
        color="secondary"
        @click="showAll = true"
      />
      <div class="muted release">Dismech release {{ data.release }}</div>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { uniq } from "lodash";
import { getDismechMechanisms } from "@/api/dismech";
import type { DismechMechanisms } from "@/api/dismech";
import type { Node } from "@/api/model";
import { useQuery } from "@/composables/use-query";
import { appendToBody } from "@/global/tooltip";
import { enumLabel, nodeTooltip, useDismechPreview } from "@/util/dismech";

type Props = {
  node: Node;
};

const props = defineProps<Props>();

const MAX_ROWS = 20;
const MAX_PHENOTYPES = 6;

const SLOT_LABELS: Record<string, string> = {
  gene: "gene",
  genes: "gene",
  cell_types: "cell type",
  biological_processes: "biological process",
  molecular_functions: "molecular function",
  cellular_components: "cellular component",
  locations: "location",
  chemical_entities: "chemical",
};

const slotLabel = (slot: string) => SLOT_LABELS[slot] ?? slot;

const preview = useDismechPreview();
const showAll = ref(false);

const show = computed(
  () =>
    preview.value && /^(GO|CL|UBERON|CHEBI|HGNC):/.test(props.node.id ?? ""),
);
const name = computed(() => props.node.name || data.value.label || "this term");

const { query, data, isLoading, isError } = useQuery(
  async () => await getDismechMechanisms(props.node.id),
  { id: "", release: "", rows: [], mechanism_nodes: {} } as DismechMechanisms,
);

const diseases = computed(() => uniq(data.value.rows.map((r) => r.disorder)));
const visibleRows = computed(() =>
  showAll.value ? data.value.rows : data.value.rows.slice(0, MAX_ROWS),
);

watch(
  () => [props.node.id, show.value],
  () => {
    showAll.value = false;
    if (show.value) query();
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.mechanisms {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 15px;
}

.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 25px;
}

.rows {
  width: 100%;
  border-collapse: collapse;
  text-align: left;

  th,
  td {
    padding: 8px 10px;
    border-bottom: solid 1px $light-gray;
    vertical-align: top;
  }
}

.mechanism {
  padding: 1px 6px;
  border: solid 1px $theme;
  border-radius: 4px;
  cursor: help;
}

.chip {
  display: inline-block;
  margin: 0 4px 4px 0;
  padding: 1px 8px;
  border-radius: 999px;
  background: $light-gray;
  font-size: 0.85em;
}

.chip.diagnostic {
  background: $theme;
  color: $white;
}

.muted {
  color: $dark-gray;
  font-size: 0.9em;
}

.ai {
  color: $theme;
}

.release {
  align-self: flex-end;
}
</style>
