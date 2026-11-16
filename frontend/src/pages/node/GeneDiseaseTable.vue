<!--
  experimental: KG causal or correlated gene-disease associations collapsed
  across sources, with dismech's genetics records for each pair and the gene's
  mechanisms in that disease. on a gene page the rows are diseases; on a
  disease page, genes.
-->

<template>
  <AppStatus v-if="isLoading && !profile.rows.length" code="loading"
    >Loading {{ rowNoun }}s</AppStatus
  >
  <AppStatus v-else-if="isError" code="error"
    >Error loading {{ rowNoun }}s</AppStatus
  >
  <div v-else class="profile">
    <div class="summary">
      <span
        ><strong>{{ plural(profile.kg_total, rowNoun) }}</strong> in
        Monarch</span
      >
      <span>
        <AppIcon icon="robot" class="ai" />
        {{ profile.dismech_corroborated.toLocaleString() }} corroborated by
        Dismech
        <span class="muted">(AI-assisted curation, may have mistakes)</span>
      </span>
      <AppCheckbox
        v-if="profile.dismech_corroborated"
        v-model="onlyCorroborated"
        text="Only Dismech-corroborated"
      />
      <AppCheckbox
        v-if="profile.dismech_unmatched"
        v-model="showDismechOnly"
        :text="`Show ${profile.dismech_unmatched.toLocaleString()} Dismech-only ${rowNoun}s`"
      />
    </div>

    <table class="rows">
      <thead>
        <tr>
          <th>{{ byGene ? "Disease" : "Gene" }}</th>
          <th>Sources</th>
          <th>Dismech</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="row in profile.rows" :key="rowId(row)">
          <tr :class="{ 'dismech-only': row.dismech_only }">
            <td>
              <AppNodeBadge
                :node="{
                  id: rowId(row),
                  name: row.label ?? rowId(row),
                  category: byGene ? 'biolink:Disease' : 'biolink:Gene',
                }"
              />
            </td>
            <td class="chips">
              <span v-if="row.dismech_only" class="muted"
                >Not in Monarch's gene associations</span
              >
              <span
                v-for="source in row.sources"
                :key="source"
                v-tooltip="recordsFor(row, source)"
                class="chip"
                >{{ sourceLabel(source) }}</span
              >
            </td>
            <td>
              <template v-if="row.dismech.length">
                <span
                  v-tooltip="'Dismech: AI-assisted curation, may have mistakes'"
                  class="chip dismech"
                  ><AppIcon icon="robot" /> Dismech</span
                >
                <div v-for="m in row.dismech" :key="m.disorder_file">
                  {{ relationship(m) }}
                  <span
                    v-for="v in m.validity"
                    :key="v.classified_by ?? ''"
                    class="muted"
                    >· {{ enumLabel(v.classified_by) }}
                    {{ enumLabel(v.classification) }}</span
                  >
                </div>
              </template>
            </td>
            <td>
              <AppButton
                v-if="row.dismech.length"
                v-tooltip="'Show mechanism and Dismech evidence'"
                :icon="expanded[rowId(row)] ? 'angle-up' : 'angle-down'"
                design="small"
                color="secondary"
                @click="expanded[rowId(row)] = !expanded[rowId(row)]"
              />
            </td>
          </tr>
          <tr v-if="expanded[rowId(row)]" class="detail">
            <td colspan="4">
              <template v-if="hasGraph(row)">
                <MechanismDag
                  :nodes="graph(row).nodes"
                  :edges="graph(row).edges"
                />
                <div v-if="graph(row).hidden" class="muted">
                  {{ plural(graph(row).hidden, "more node") }} downstream; see
                  the full pathograph below
                </div>
              </template>
              <div v-else class="muted">
                No mechanisms in Dismech name this gene
              </div>
              <div
                v-for="m in row.dismech"
                :key="m.disorder_file"
                class="match"
              >
                <p v-if="m.notes" class="notes">{{ m.notes }}</p>
                <ul class="evidence">
                  <li v-for="e in m.evidence" :key="e.reference + e.snippet">
                    <AppLink
                      v-if="e.reference.startsWith('PMID:')"
                      :to="`https://pubmed.ncbi.nlm.nih.gov/${e.reference.slice(5)}`"
                      >{{ e.reference }}</AppLink
                    >
                    <span v-else>{{ e.reference }}</span>
                    <q v-if="e.snippet">{{ e.snippet }}</q>
                  </li>
                </ul>
                <div class="links">
                  <AppLink
                    class="muted"
                    :to="dismechDisorderUrl(m.disorder_file)"
                    >View {{ m.disorder }} on Dismech</AppLink
                  >
                  <DismechFeedback :record="feedbackRecord(row, m)" />
                </div>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    <TheTableControls
      v-model:per-page="perPage"
      v-model:start="start"
      :rows="profile.rows"
      :total="profile.total"
      :show-download="false"
    />
    <div class="muted release">Dismech release {{ profile.release }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { getGeneDiseaseProfile } from "@/api/dismech";
import type {
  DismechGene,
  GeneDiseaseProfile,
  GeneDiseaseRow,
} from "@/api/dismech";
import type { Node } from "@/api/model";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import TheTableControls from "@/components/TheTableContols.vue";
import { useQuery } from "@/composables/use-query";
import DismechFeedback from "@/pages/node/DismechFeedback.vue";
import MechanismDag from "@/pages/node/MechanismDag.vue";
import type { DagEdge, DagNode } from "@/pages/node/MechanismDag.vue";
import {
  dismechDisorderUrl,
  enumLabel,
  nodeTooltip,
  plural,
  sourceLabel,
  trimGraph,
} from "@/util/dismech";
import type { DismechFeedbackRecord } from "@/util/dismech-feedback";
import { labeledChain } from "@/util/dismech-feedback";

type Props = {
  node: Node;
  kind: "causal" | "correlated";
};

const props = defineProps<Props>();

/** gene page: rows are diseases. disease page: rows are genes */
const byGene = computed(() => props.node.category === "biolink:Gene");
const rowNoun = computed(() => (byGene.value ? "disease" : "gene"));

const onlyCorroborated = ref(false);
/** dismech-only pairs are opt in: no OMIM/Orphanet/ClinGen association */
const showDismechOnly = ref(false);
const perPage = ref(10);
const start = ref(0);
const expanded = ref<Record<string, boolean>>({});

const rowId = (row: GeneDiseaseRow) => row.disease_id ?? row.gene_id ?? "";

/** dismech's relationship, e.g. Causative, or its free-text association */
const relationship = (m: DismechGene) =>
  enumLabel(m.relationship_type) || m.association || "Associated";

/** original records and predicates behind a source chip */
const recordsFor = (row: GeneDiseaseRow, source: string) =>
  row.observations
    .filter((o) => o.source === source)
    .map((o) =>
      [o.predicate.replace("biolink:", "").replace(/_/g, " "), o.record]
        .filter(Boolean)
        .join(" · "),
    )
    .join(", ");

/** a dismech genetics record, as it appears in this row, for feedback */
const feedbackRecord = (
  row: GeneDiseaseRow,
  m: DismechGene,
): DismechFeedbackRecord => ({
  kind: "gene",
  claim: `${m.disorder}: ${m.symbol}`,
  disorder: m.disorder,
  disorder_file: m.disorder_file,
  release: profile.value.release,
  fields: [
    ["Gene", `${m.symbol} (${m.gene_id})`],
    ["Relationship", relationship(m)],
    ...m.validity.map(
      (v) =>
        [
          "Validity",
          `${enumLabel(v.classified_by)} ${enumLabel(v.classification)}`,
        ] as [string, string],
    ),
    ...(m.notes ? [["Notes", m.notes] as [string, string]] : []),
    ["Monarch section", `${props.kind} genes`],
    [
      "Monarch sources",
      row.dismech_only ? "None; Dismech only" : row.sources.join(", "),
    ],
  ],
  evidence: m.evidence,
  chain: labeledChain(m.edges, profile.value.mechanism_nodes),
});

const hasGraph = (row: GeneDiseaseRow) =>
  row.dismech.some((m) => m.mechanisms.length);

/** the gene's mechanisms (emphasized) and the paths from them to phenotypes */
const graph = (row: GeneDiseaseRow) => {
  const nodes = profile.value.mechanism_nodes;
  const focus = new Set(
    row.dismech.flatMap((m) => m.mechanisms.map((x) => x.node_id)),
  );
  const edges = new Map<string, DagEdge>();
  for (const m of row.dismech)
    for (const e of m.edges)
      edges.set(`${e.source}>${e.target}`, {
        source: e.source,
        target: e.target,
        linkType: e.link_type,
      });
  const ids = new Set([
    ...focus,
    ...[...edges.values()].flatMap((e) => [e.source, e.target]),
  ]);
  const dagNodes: DagNode[] = [...ids].map((id) => ({
    id,
    label: nodes[id]?.name ?? id,
    kind: nodes[id]?.kind === "phenotype" ? "phenotype" : "mechanism",
    tooltip: nodeTooltip(nodes, id, nodes[id]?.kind === "phenotype"),
    focus: focus.has(id),
  }));
  return trimGraph(dagNodes, [...edges.values()]);
};

const {
  query: runGetProfile,
  data: profile,
  isLoading,
  isError,
} = useQuery(
  async () =>
    await getGeneDiseaseProfile(props.node.id, props.kind, {
      corroboratedOnly: onlyCorroborated.value,
      dismechOnly: showDismechOnly.value,
      limit: perPage.value,
      offset: start.value,
    }),
  {
    id: "",
    release: "",
    kind: "causal",
    total: 0,
    rows: [],
    dismech_available: false,
    kg_total: 0,
    dismech_corroborated: 0,
    dismech_unmatched: 0,
    mechanism_nodes: {},
  } as GeneDiseaseProfile,
);

watch([onlyCorroborated, showDismechOnly], () => {
  if (start.value) start.value = 0;
  else runGetProfile();
});
watch([perPage, start], runGetProfile);
watch(
  () => [props.node.id, props.kind],
  () => {
    expanded.value = {};
    if (start.value) start.value = 0;
    else runGetProfile();
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.profile {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 15px;
}

.summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 25px;
}

.muted {
  color: $dark-gray;
  font-size: 0.9em;
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

.dismech-only > td:first-child {
  border-left: dashed 2px $theme;
}

.chips {
  white-space: nowrap;
}

.chip {
  display: inline-block;
  margin: 0 4px 4px 0;
  padding: 1px 8px;
  border-radius: 999px;
  background: $light-gray;
  font-size: 0.85em;
}

.chip.dismech,
.ai {
  color: $theme;
}

.detail td {
  background: $off-white;
}

.match + .match {
  margin-top: 15px;
  padding-top: 15px;
  border-top: dashed 1px $light-gray;
}

.links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.notes {
  margin: 8px 0;
}

.evidence {
  margin: 8px 0;
  padding-left: 20px;

  q {
    margin-left: 6px;
    color: $dark-gray;
    font-style: italic;
  }
}

.release {
  align-self: flex-end;
}
</style>
