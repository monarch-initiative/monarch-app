<!--
  experimental: KG phenotype associations collapsed across primary knowledge
  sources, with dismech corroboration and the mechanism chain behind each row.
  on a disease page the rows are its phenotypes; on a phenotype page, the
  diseases that have it.
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
      <span v-if="!profile.kg_total && profile.dismech_unmatched">
        <AppIcon icon="robot" class="ai" />
        <strong>{{ plural(profile.dismech_unmatched, rowNoun) }}</strong> from
        Dismech only
        <span class="muted">(AI-assisted curation, may have mistakes)</span>
      </span>
      <template v-else>
        <span
          ><strong>{{ plural(profile.kg_total, rowNoun) }}</strong> in
          Monarch</span
        >
        <span v-if="profile.dismech_available">
          <AppIcon icon="robot" class="ai" />
          {{ profile.dismech_corroborated.toLocaleString() }} corroborated by
          Dismech
          <span class="muted">(AI-assisted curation, may have mistakes)</span>
        </span>
      </template>
      <AppCheckbox
        v-if="profile.dismech_corroborated"
        v-model="onlyCorroborated"
        text="Only Dismech-corroborated"
      />
      <AppCheckbox
        v-if="profile.kg_total && profile.dismech_unmatched"
        v-model="showDismechOnly"
        :text="`Show ${profile.dismech_unmatched.toLocaleString()} Dismech-only ${rowNoun}s`"
      />
    </div>

    <table class="rows">
      <thead>
        <tr>
          <th>{{ rowLabel }}</th>
          <th>Sources</th>
          <th>Frequency</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="row in profile.rows" :key="rowKey(row)">
          <tr
            :class="{ negated: row.negated, 'dismech-only': row.dismech_only }"
          >
            <td>
              <AppLink :to="`/${rowId(row)}`">{{ row.label }}</AppLink>
              <span v-if="row.negated" class="badge not">NOT</span>
              <span v-if="isDiagnostic(row)" class="badge diagnostic"
                >diagnostic</span
              >
              <div class="muted id">{{ rowId(row) }}</div>
            </td>
            <td class="chips">
              <span
                v-for="source in row.sources"
                :key="source"
                v-tooltip="recordsFor(row, source)"
                class="chip"
                >{{ sourceLabel(source) }}</span
              >
              <span
                v-if="row.dismech.length"
                v-tooltip="'Dismech: AI-assisted curation, may have mistakes'"
                class="chip dismech"
                ><AppIcon icon="robot" /> Dismech</span
              >
            </td>
            <td class="frequency">
              <template v-if="row.dismech_only">
                <div v-for="(f, i) in dismechFrequencies(row)" :key="i">
                  <span class="muted">Dismech</span> {{ f }}
                </div>
                <div v-if="profile.kg_total" class="muted">
                  Not in OMIM or Orphanet annotations
                </div>
              </template>
              <div v-for="(f, i) in frequencies(row)" :key="i">
                <span class="muted">{{ f.source }}</span> {{ f.text }}
              </div>
            </td>
            <td>
              <AppButton
                v-if="row.dismech.length"
                v-tooltip="'Show mechanism and Dismech evidence'"
                :icon="expanded[rowKey(row)] ? 'angle-up' : 'angle-down'"
                design="small"
                color="secondary"
                @click="expanded[rowKey(row)] = !expanded[rowKey(row)]"
              />
            </td>
          </tr>
          <tr v-if="expanded[rowKey(row)]" class="detail">
            <td colspan="4">
              <MechanismDag
                v-if="graph(row).edges.length"
                v-bind="graph(row)"
              />
              <div v-else class="muted">No mechanism chain curated</div>
              <div
                v-for="m in row.dismech"
                :key="m.phenotype_node_id"
                class="match"
              >
                <div class="refines">
                  <template v-if="refines(m)">
                    Dismech records the more specific
                    <AppLink :to="`/${m.hpo_id}`">{{
                      m.hpo_label || m.hpo_id
                    }}</AppLink>
                  </template>
                  <template v-else>Dismech evidence</template>
                  <span v-if="m.frequency_hp || m.frequency_text" class="muted">
                    &middot;
                    {{
                      FREQUENCY_LABELS[m.frequency_hp ?? ""] ?? m.frequency_text
                    }}
                  </span>
                </div>
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
                <DismechFeedback :record="feedbackRecord(row, m)" />
              </div>
              <AppLink
                v-for="d in disorders(row)"
                :key="d.file"
                class="muted"
                :to="dismechDisorderUrl(d.file)"
                >View {{ d.name }} on Dismech</AppLink
              >
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
import { uniq, uniqBy } from "lodash";
import { getPhenotypeDiseases, getPhenotypeProfile } from "@/api/dismech";
import type {
  DismechMatch,
  PhenotypeProfile,
  PhenotypeProfileRow,
} from "@/api/dismech";
import type { Node } from "@/api/model";
import AppCheckbox from "@/components/AppCheckbox.vue";
import TheTableControls from "@/components/TheTableContols.vue";
import { useQuery } from "@/composables/use-query";
import DismechFeedback from "@/pages/node/DismechFeedback.vue";
import MechanismDag from "@/pages/node/MechanismDag.vue";
import {
  dismechDisorderUrl,
  FREQUENCY_LABELS,
  mechanismGraph,
  plural,
  sourceLabel,
} from "@/util/dismech";
import type { DismechFeedbackRecord } from "@/util/dismech-feedback";
import { labeledChain } from "@/util/dismech-feedback";

type Props = {
  node: Node;
  /** start with dismech-only rows shown, when the KG has none */
  dismechOnly?: boolean;
};

const props = defineProps<Props>();

/** disease page: rows are phenotypes. phenotype page: rows are diseases */
const byDisease = computed(() => props.node.category === "biolink:Disease");
const rowNoun = computed(() => (byDisease.value ? "phenotype" : "disease"));
const rowLabel = computed(() => (byDisease.value ? "Phenotype" : "Disease"));

const onlyCorroborated = ref(false);
/** dismech-only rows are opt in: they have no OMIM/Orphanet corroboration */
const showDismechOnly = ref(props.dismechOnly ?? false);
const perPage = ref(10);
const start = ref(0);
const expanded = ref<Record<string, boolean>>({});

const rowId = (row: PhenotypeProfileRow) => row.hpo_id ?? row.disease_id ?? "";

const rowKey = (row: PhenotypeProfileRow) =>
  `${rowId(row)}${row.negated ? ":not" : ""}`;

/** dismech's record names a subclass of the row's (or the page's) phenotype */
const refines = (m: DismechMatch) =>
  byDisease.value ? m.match === "more_specific" : m.hpo_id !== props.node.id;

const disorders = (row: PhenotypeProfileRow) =>
  uniqBy(
    row.dismech.map((m) => ({ file: m.disorder_file, name: m.disorder })),
    "file",
  );

const isDiagnostic = (row: PhenotypeProfileRow) =>
  row.dismech.some((m) => m.diagnostic);

/** original records behind a source chip, e.g. OMIM:277900 */
const recordsFor = (row: PhenotypeProfileRow, source: string) =>
  row.observations
    .filter((o) => o.source === source && o.record)
    .map((o) => o.record)
    .join(", ");

/** one frequency line per source, kept separate since sources often disagree */
const frequencies = (row: PhenotypeProfileRow) =>
  row.observations
    .map((o) => {
      let text = "";
      if (o.count != null && o.total != null)
        text = `${o.count}/${o.total} (${Math.round((o.count / o.total) * 100)}%)`;
      else if (o.percentage != null) text = `${o.percentage}%`;
      else if (o.frequency_label) text = o.frequency_label;
      return { source: sourceLabel(o.source), text };
    })
    .filter((f) => f.text);

/** dismech's frequencies, for a row no KG source annotates */
const dismechFrequencies = (row: PhenotypeProfileRow) =>
  uniq(
    row.dismech
      .map((m) => FREQUENCY_LABELS[m.frequency_hp ?? ""] ?? m.frequency_text)
      .filter(Boolean),
  );

const MATCH_TEXT: Record<DismechMatch["match"], string> = {
  exact: "Same term",
  more_specific: "Refines this term",
  dismech_only: "Dismech only; no OMIM or Orphanet annotation",
};

/** a dismech phenotype record, as it appears in this row, for feedback */
const feedbackRecord = (
  row: PhenotypeProfileRow,
  m: DismechMatch,
): DismechFeedbackRecord => {
  const frequency = FREQUENCY_LABELS[m.frequency_hp ?? ""] ?? m.frequency_text;
  return {
    kind: "phenotype",
    claim: `${m.disorder}: ${m.hpo_label || m.phenotype_name}`,
    disorder: m.disorder,
    disorder_file: m.disorder_file,
    release: profile.value.release,
    fields: [
      ["Phenotype", `${m.phenotype_name} (${m.hpo_id})`],
      ...(frequency ? [["Frequency", frequency] as [string, string]] : []),
      ...(m.diagnostic ? [["Diagnostic", "Yes"] as [string, string]] : []),
      ["Monarch row", `${row.label ?? rowId(row)} (${rowId(row)})`],
      ["Match", MATCH_TEXT[m.match]],
    ],
    evidence: m.evidence,
    chain: labeledChain(m.upstream_edges, profile.value.mechanism_nodes),
    diagnostic: m.diagnostic,
  };
};

const graph = (row: PhenotypeProfileRow) =>
  mechanismGraph(row.dismech, profile.value.mechanism_nodes);

const {
  query: runGetProfile,
  data: profile,
  isLoading,
  isError,
} = useQuery(
  async () => {
    const options = {
      corroboratedOnly: onlyCorroborated.value,
      dismechOnly: showDismechOnly.value,
      limit: perPage.value,
      offset: start.value,
    };
    return byDisease.value
      ? await getPhenotypeProfile(props.node.id, options)
      : await getPhenotypeDiseases(props.node.id, options);
  },
  {
    id: "",
    release: "",
    total: 0,
    rows: [],
    dismech_available: false,
    kg_total: 0,
    dismech_corroborated: 0,
    dismech_unmatched: 0,
    mechanism_nodes: {},
  } as PhenotypeProfile,
);

watch([onlyCorroborated, showDismechOnly], () => {
  if (start.value) start.value = 0;
  else runGetProfile();
});
watch([perPage, start], runGetProfile);
watch(
  () => props.node.id,
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

.id {
  font-family: monospace;
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

.negated {
  opacity: 0.6;
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

.badge {
  margin-left: 6px;
  padding: 0 6px;
  border-radius: 3px;
  font-size: 0.75em;
  text-transform: uppercase;
}

.badge.diagnostic {
  background: $theme;
  color: $white;
}

.badge.not {
  background: $error;
  color: $white;
}

.detail td {
  background: $off-white;
}

.match + .match {
  margin-top: 15px;
  padding-top: 15px;
  border-top: dashed 1px $light-gray;
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
