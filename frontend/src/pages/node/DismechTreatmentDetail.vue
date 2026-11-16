<!--
  dismech's account of one or more treatments in a drug section row: the
  mechanisms each targets (with pathograph hover details), the phenotypes it
  treats, and its evidence
-->

<template>
  <div class="dismech-treatments">
    <div class="head">
      <AppIcon icon="robot" class="ai" /> Dismech
      <span class="muted">(AI-assisted curation, may have mistakes)</span>
    </div>
    <div v-for="t in treatments" :key="t.treatment_node_id" class="treatment">
      <div class="title">
        <strong>{{ t.name }}</strong>
        <span v-if="showDisease" class="muted">
          for
          <AppLink v-if="t.mondo_id" :to="`/${t.mondo_id}`">{{
            t.disorder
          }}</AppLink>
          <template v-else>{{ t.disorder }}</template>
        </span>
        <span v-if="t.modality" class="pill">{{ enumLabel(t.modality) }}</span>
      </div>
      <div v-for="m in t.target_mechanisms" :key="m.node_id" class="target">
        <span class="effect">{{ enumLabel(m.effect) || "Targets" }}</span>
        <span
          v-tooltip="
            m.resolved
              ? {
                  content: nodeTooltip(nodes, m.node_id),
                  allowHTML: true,
                  maxWidth: 360,
                  interactive: true,
                  appendTo: appendToBody,
                }
              : 'Not a mechanism recorded for this disorder'
          "
          :class="['mechanism', { unresolved: !m.resolved }]"
          tabindex="0"
          >{{ m.name }}</span
        >
      </div>
      <div v-if="t.target_phenotypes.length" class="target">
        <span class="effect">Treats</span>
        <template v-for="(p, i) in t.target_phenotypes" :key="p.hpo_id">
          <span v-if="i" class="muted">, </span>
          <AppLink :to="`/${p.hpo_id}`">{{ p.label || p.hpo_id }}</AppLink>
        </template>
      </div>
      <p v-if="t.description" class="description">{{ t.description }}</p>
      <div class="links">
        <a
          v-for="e in t.evidence.filter((e) => e.reference.startsWith('PMID:'))"
          :key="e.reference"
          v-tooltip="e.snippet ?? ''"
          :href="`https://pubmed.ncbi.nlm.nih.gov/${e.reference.slice(5)}`"
          target="_blank"
          rel="noopener"
          >{{ e.reference }}</a
        >
        <a
          :href="dismechDisorderUrl(t.disorder_file)"
          target="_blank"
          rel="noopener"
          >View on Dismech</a
        >
        <DismechFeedback :record="feedbackRecord(t)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DismechTreatment, MechanismNode } from "@/api/dismech";
import { appendToBody } from "@/global/tooltip";
import DismechFeedback from "@/pages/node/DismechFeedback.vue";
import { dismechDisorderUrl, enumLabel, nodeTooltip } from "@/util/dismech";
import type { DismechFeedbackRecord } from "@/util/dismech-feedback";

type Props = {
  treatments: DismechTreatment[];
  nodes: Record<string, MechanismNode>;
  release: string;
  /** the section row the treatments are matched to, if any */
  monarchRow?: string;
  /** name the disease each treatment is for (on a drug page) */
  showDisease?: boolean;
};

const props = defineProps<Props>();

/** a dismech treatment record, as it appears here, for feedback */
const feedbackRecord = (t: DismechTreatment): DismechFeedbackRecord => ({
  kind: "treatment",
  claim: `${t.disorder}: ${t.name}`,
  disorder: t.disorder,
  disorder_file: t.disorder_file,
  release: props.release,
  fields: [
    ...(t.modality
      ? [["Modality", enumLabel(t.modality)] as [string, string]]
      : []),
    ...(t.agents.length
      ? [
          [
            "Agents",
            t.agents.map((a) => `${a.label ?? a.id} (${a.id})`).join(", "),
          ] as [string, string],
        ]
      : []),
    ...t.target_mechanisms.map(
      (m) =>
        [
          enumLabel(m.effect) || "Targets",
          `${m.name}${m.resolved ? "" : " (not a mechanism in this disorder)"}`,
        ] as [string, string],
    ),
    ...(t.target_phenotypes.length
      ? [
          [
            "Treats",
            t.target_phenotypes
              .map((p) => `${p.label || p.hpo_id} (${p.hpo_id})`)
              .join(", "),
          ] as [string, string],
        ]
      : []),
    ...(t.description
      ? [["Description", t.description] as [string, string]]
      : []),
    ["Monarch row", props.monarchRow ?? "None; not matched to an indication"],
  ],
  evidence: t.evidence,
  chain: [],
});
</script>

<style lang="scss" scoped>
.dismech-treatments {
  display: flex;
  flex-direction: column;
  margin: 10px 0;
  padding: 10px 15px;
  gap: 12px;
  border-left: solid 3px $theme;
  background: $off-white;
}

.head {
  font-weight: 600;
}

.treatment {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title,
.links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.pill {
  padding: 0 6px;
  border-radius: 999px;
  background: $light-gray;
  font-size: 0.85em;
}

.effect {
  margin-right: 6px;
  font-weight: 600;
}

.mechanism {
  text-decoration: underline dotted;
  cursor: help;
}

.mechanism.unresolved {
  text-decoration-style: dashed;
}

.description {
  margin: 0;
}

.muted {
  color: $dark-gray;
  font-weight: normal;
  font-size: 0.9em;
}

.ai {
  color: $theme;
}
</style>
