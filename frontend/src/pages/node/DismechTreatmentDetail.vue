<!--
  dismech's record behind one treatment statement in a drug section, laid out
  like the section's own assertions: a source heading, the mechanism graph from
  the treatment through its targets to phenotypes, then the supporting texts
-->

<template>
  <div class="dismech-block">
    <h4 class="head">
      <AppIcon icon="robot" class="ai" /> Dismech
      <span class="muted"
        >{{ plural(references, "reference") }} · AI-assisted curation, may have
        mistakes</span
      >
    </h4>
    <template v-if="graph.edges.length">
      <MechanismDag :nodes="graph.nodes" :edges="graph.edges" />
      <div v-if="graph.hidden" class="muted">
        {{ plural(graph.hidden, "more node") }} downstream
      </div>
    </template>
    <div v-if="unresolved.length" class="muted">
      Also targets {{ unresolved.join(", ") }}, not a mechanism recorded for
      this disorder
    </div>
    <div class="assertion">
      <p class="supporting">
        <strong>{{ treatment.name }}</strong>
        <span v-if="treatment.modality" class="muted">
          · {{ enumLabel(treatment.modality) }}</span
        ><template v-if="treatment.description">
          · {{ treatment.description }}</template
        >
      </p>
    </div>
    <div v-for="e in snippets" :key="e.reference + e.snippet" class="assertion">
      <p class="supporting">{{ e.snippet }}</p>
      <div class="assertion-links">
        <a
          v-if="e.reference.startsWith('PMID:')"
          :href="`https://pubmed.ncbi.nlm.nih.gov/${e.reference.slice(5)}`"
          target="_blank"
          rel="noopener"
          >{{ e.reference }}</a
        >
        <span v-else>{{ e.reference }}</span>
      </div>
    </div>
    <div class="assertion-links">
      <a
        v-for="pmid in pmids.filter((p) => !snippetRefs.has(p))"
        :key="pmid"
        :href="`https://pubmed.ncbi.nlm.nih.gov/${pmid.slice(5)}`"
        target="_blank"
        rel="noopener"
        >{{ pmid }}</a
      >
      <a
        :href="dismechDisorderUrl(treatment.disorder_file)"
        target="_blank"
        rel="noopener"
        >View {{ treatment.disorder }} on Dismech</a
      >
      <DismechFeedback :record="feedbackRecord" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { uniq, uniqBy } from "lodash";
import type { DismechTreatment, MechanismNode } from "@/api/dismech";
import DismechFeedback from "@/pages/node/DismechFeedback.vue";
import MechanismDag from "@/pages/node/MechanismDag.vue";
import {
  dismechDisorderUrl,
  enumLabel,
  plural,
  treatmentGraph,
} from "@/util/dismech";
import type { DismechFeedbackRecord } from "@/util/dismech-feedback";
import { labeledChain } from "@/util/dismech-feedback";

type Props = {
  treatment: DismechTreatment;
  nodes: Record<string, MechanismNode>;
  release: string;
  /** the section row the treatment is matched to, if any */
  monarchRow?: string;
};

const props = defineProps<Props>();

const graph = computed(() => treatmentGraph(props.treatment, props.nodes));

const unresolved = computed(() =>
  props.treatment.target_mechanisms
    .filter((m) => !m.resolved)
    .map((m) => m.name),
);

/** the treatment's evidence and its targets', one entry per quote */
const evidence = computed(() =>
  uniqBy(
    [
      ...props.treatment.evidence,
      ...props.treatment.target_mechanisms.flatMap((m) => m.evidence),
    ],
    (e) => e.reference + e.snippet,
  ),
);
const snippets = computed(() => evidence.value.filter((e) => e.snippet));
const snippetRefs = computed(
  () => new Set(snippets.value.map((e) => e.reference)),
);
const pmids = computed(() =>
  uniq(
    evidence.value.map((e) => e.reference).filter((r) => r.startsWith("PMID:")),
  ),
);

const references = computed(
  () => new Set(evidence.value.map((e) => e.reference)).size,
);

const pair = (key: string, value: string): [string, string] => [key, value];

/** this treatment record, as it appears here, for feedback */
const feedbackRecord = computed((): DismechFeedbackRecord => {
  const t = props.treatment;
  return {
    kind: "treatment",
    claim: `${t.disorder}: ${t.name}`,
    disorder: t.disorder,
    disorder_file: t.disorder_file,
    release: props.release,
    fields: [
      ...(t.modality ? [pair("Modality", enumLabel(t.modality))] : []),
      ...(t.agents.length
        ? [
            pair(
              "Agents",
              t.agents.map((a) => `${a.label ?? a.id} (${a.id})`).join(", "),
            ),
          ]
        : []),
      ...t.target_mechanisms.map((m) =>
        pair(
          enumLabel(m.effect) || "Targets",
          `${m.name}${m.resolved ? "" : " (not a mechanism in this disorder)"}`,
        ),
      ),
      ...(t.target_phenotypes.length
        ? [
            pair(
              "Treats",
              t.target_phenotypes
                .map((p) => `${p.label || p.hpo_id} (${p.hpo_id})`)
                .join(", "),
            ),
          ]
        : []),
      ...(t.description ? [pair("Description", t.description)] : []),
      pair("Monarch row", props.monarchRow ?? "None; Dismech only"),
    ],
    evidence: evidence.value,
    chain: [
      ...t.target_mechanisms
        .filter((m) => m.resolved)
        .map((m) => ({
          source: t.name,
          target: props.nodes[m.node_id]?.name ?? m.name,
        })),
      ...labeledChain(t.edges, props.nodes),
    ],
  };
});
</script>

<style lang="scss" scoped>
/* matches the drug section's own assertion blocks */
.dismech-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.head {
  margin: 4px 0 0;
  font-size: 0.95rem;
}

.assertion {
  align-self: stretch;
  padding: 8px 10px;
  border-radius: $rounded;
  background: $off-white;
}

.supporting {
  margin: 0;
  font-size: 0.85rem;
}

.assertion-links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 4px;
  gap: 4px 10px;
  font-size: 0.8rem;
}

.muted {
  color: $dark-gray;
  font-weight: normal;
  font-size: 0.85rem;
}

.ai {
  color: $theme;
}
</style>
