<!--
  experimental: diseases whose dismech mechanisms involve this node's GO
  process, CL cell type or UBERON location, one row per disease, with the
  phenotypes those mechanisms lead to. self-hides when there are none.
-->

<template>
  <AppSection
    v-if="show && (isLoading || data.total)"
    width="full"
    class="inset"
    alignment="left"
  >
    <AppHeading :level="3">Disease Mechanisms</AppHeading>
    <AppStatus v-if="isLoading && !data.rows.length" code="loading"
      >Loading diseases</AppStatus
    >
    <AppStatus v-else-if="isError" code="error"
      >Error loading diseases</AppStatus
    >
    <div v-else class="diseases">
      <div class="summary">
        <span
          ><strong>{{ plural(data.total, "disease") }}</strong> with mechanisms
          involving {{ name }}</span
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
            <th>Mechanisms</th>
            <th>Leads to</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="row in data.rows" :key="row.disorder_file">
            <tr>
              <td>
                <AppNodeBadge
                  v-if="row.disease_id"
                  :node="{
                    id: row.disease_id,
                    name: row.label,
                    category: 'biolink:Disease',
                  }"
                />
                <span v-else>{{ row.label }}</span>
              </td>
              <td>
                <div
                  v-for="m in row.mechanisms.slice(0, MAX_MECHANISMS)"
                  :key="m.node_id"
                >
                  <span
                    v-tooltip="tooltip(m.node_id)"
                    class="mechanism"
                    tabindex="0"
                    >{{ m.name }}</span
                  >
                </div>
                <div
                  v-if="row.mechanisms.length > MAX_MECHANISMS"
                  class="muted"
                >
                  +{{ row.mechanisms.length - MAX_MECHANISMS }} more
                </div>
                <div class="muted">
                  as {{ row.slots.map(slotLabel).join(", ") }}
                </div>
              </td>
              <td class="chips">
                <AppLink
                  v-for="p in row.leads_to.slice(0, MAX_PHENOTYPES)"
                  :key="p.hpo_id"
                  v-tooltip="p.diagnostic ? 'Diagnostic for this disease' : ''"
                  :to="`/${p.hpo_id}`"
                  :class="['chip', { diagnostic: p.diagnostic }]"
                  >{{ p.label || p.hpo_id }}</AppLink
                >
                <span v-if="row.leads_to.length > MAX_PHENOTYPES" class="muted"
                  >+{{ row.leads_to.length - MAX_PHENOTYPES }} more</span
                >
              </td>
              <td>
                <AppButton
                  v-tooltip="'Show mechanism graph'"
                  :icon="
                    expanded[row.disorder_file] ? 'angle-up' : 'angle-down'
                  "
                  design="small"
                  color="secondary"
                  @click="
                    expanded[row.disorder_file] = !expanded[row.disorder_file]
                  "
                />
              </td>
            </tr>
            <tr v-if="expanded[row.disorder_file]" class="detail">
              <td colspan="4">
                <template v-if="row.edges.length">
                  <MechanismDag
                    :nodes="graph(row).nodes"
                    :edges="graph(row).edges"
                  />
                  <div v-if="graph(row).hidden" class="muted">
                    {{ plural(graph(row).hidden, "more node") }} downstream
                  </div>
                </template>
                <div v-else class="muted">
                  No phenotypes curated downstream of these mechanisms
                </div>
                <div class="links">
                  <AppLink
                    class="muted"
                    :to="dismechDisorderUrl(row.disorder_file)"
                    >View {{ row.disorder }} on Dismech</AppLink
                  >
                  <DismechFeedback :record="feedbackRecord(row)" />
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <TheTableControls
        v-model:per-page="perPage"
        v-model:start="start"
        :rows="data.rows"
        :total="data.total"
        :show-download="false"
      />
      <div class="muted release">Dismech release {{ data.release }}</div>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { getTermDiseases } from "@/api/dismech";
import type { TermDisease, TermDiseases } from "@/api/dismech";
import type { Node } from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import TheTableControls from "@/components/TheTableContols.vue";
import { useQuery } from "@/composables/use-query";
import { appendToBody } from "@/global/tooltip";
import DismechFeedback from "@/pages/node/DismechFeedback.vue";
import MechanismDag from "@/pages/node/MechanismDag.vue";
import type { DagNode } from "@/pages/node/MechanismDag.vue";
import {
  dismechDisorderUrl,
  nodeTooltip,
  plural,
  trimGraph,
  useDismech,
} from "@/util/dismech";
import type { DismechFeedbackRecord } from "@/util/dismech-feedback";
import { labeledChain } from "@/util/dismech-feedback";

type Props = {
  node: Node;
};

const props = defineProps<Props>();

const MAX_MECHANISMS = 3;
const MAX_PHENOTYPES = 6;

const SLOT_LABELS: Record<string, string> = {
  cell_types: "cell type",
  biological_processes: "biological process",
  molecular_functions: "molecular function",
  cellular_components: "cellular component",
  locations: "location",
};

const slotLabel = (slot: string) => SLOT_LABELS[slot] ?? slot;

const dismech = useDismech();
const perPage = ref(10);
const start = ref(0);
const expanded = ref<Record<string, boolean>>({});

const show = computed(
  () => dismech.value && /^(GO|CL|UBERON):/.test(props.node.id ?? ""),
);
const name = computed(() => props.node.name || data.value.label || "this term");

const tooltip = (nodeId: string) => ({
  content: nodeTooltip(data.value.mechanism_nodes, nodeId),
  allowHTML: true,
  maxWidth: 360,
  interactive: true,
  appendTo: appendToBody,
});

/** a disease's mechanisms involving this term, for feedback */
const feedbackRecord = (row: TermDisease): DismechFeedbackRecord => ({
  kind: "mechanism",
  claim: `${row.disorder}: ${name.value}`,
  disorder: row.disorder,
  disorder_file: row.disorder_file,
  release: data.value.release,
  fields: [
    [
      "Term",
      `${name.value} (${props.node.id}) as ${row.slots.map(slotLabel).join(", ")}`,
    ],
    ["Mechanisms", row.mechanisms.map((m) => m.name).join("; ")],
    ...(row.leads_to.length
      ? [
          [
            "Leads to",
            row.leads_to.map((p) => p.label || p.hpo_id).join(", "),
          ] as [string, string],
        ]
      : []),
  ],
  evidence: row.mechanisms.flatMap(
    (m) => data.value.mechanism_nodes[m.node_id]?.evidence ?? [],
  ),
  chain: labeledChain(row.edges, data.value.mechanism_nodes),
});

/** the disease's mechanisms for this term, and the paths from them to phenotypes */
const graph = (row: TermDisease) => {
  const focus = new Set(row.mechanisms.map((m) => m.node_id));
  const nodes = data.value.mechanism_nodes;
  const ids = new Set([
    ...focus,
    ...row.edges.flatMap((e) => [e.source, e.target]),
  ]);
  const dagNodes: DagNode[] = [...ids].map((id) => ({
    id,
    label: nodes[id]?.name ?? id,
    kind: nodes[id]?.kind === "phenotype" ? "phenotype" : "mechanism",
    tooltip: nodeTooltip(nodes, id, nodes[id]?.kind === "phenotype"),
    focus: focus.has(id),
  }));
  return trimGraph(
    dagNodes,
    row.edges.map((e) => ({
      source: e.source,
      target: e.target,
      linkType: e.link_type,
    })),
  );
};

const { query, data, isLoading, isError } = useQuery(
  async () =>
    await getTermDiseases(props.node.id, {
      limit: perPage.value,
      offset: start.value,
    }),
  {
    id: "",
    release: "",
    total: 0,
    rows: [],
    mechanism_nodes: {},
  } as TermDiseases,
);

watch([perPage, start], () => {
  expanded.value = {};
  if (show.value) query();
});
watch(
  () => [props.node.id, show.value],
  () => {
    expanded.value = {};
    if (start.value) start.value = 0;
    else if (show.value) query();
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.diseases {
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
  text-decoration: underline dotted;
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

.detail td {
  background: $off-white;
}

.muted {
  color: $dark-gray;
  font-size: 0.9em;
}

.ai {
  color: $theme;
}

.links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  gap: 10px;
}

.release {
  align-self: flex-end;
}
</style>
