<!--
  experimental: dismech treatments and the mechanisms they act on. on a disease
  page, the disease's treatments; on a drug page, the diseases it is used for.
  gated behind the same research-use notice as the drug sections.
-->

<template>
  <AppSection
    v-if="show && (!acknowledged || data.rows.length || isLoading)"
    width="full"
    class="inset"
    alignment="left"
  >
    <AppHeading :level="3">{{ heading }}</AppHeading>

    <AppAlert icon="circle-exclamation" class="notice">
      <div>
        <p>
          For research purposes only. This information is not intended to
          diagnose, treat, cure, or prevent any disease, and does not replace
          approved prescribing information or the advice of a healthcare
          professional.
        </p>
        <p>
          <AppIcon icon="robot" class="ai" /> From Dismech, an AI-assisted
          curation that may have mistakes.
        </p>
        <AppButton
          v-if="!acknowledged"
          class="acknowledge"
          text="I understand, show treatments"
          @click="acknowledge"
        />
      </div>
    </AppAlert>

    <template v-if="acknowledged">
      <AppStatus v-if="isLoading" code="loading">Loading treatments</AppStatus>
      <AppStatus v-else-if="isError" code="error"
        >Error loading treatments</AppStatus
      >
      <div v-else class="treatments">
        <div
          v-for="t in data.rows"
          :key="t.treatment_node_id"
          class="treatment"
        >
          <div class="title">
            <strong>{{ t.name }}</strong>
            <template v-if="!byDisease && t.mondo_id">
              <span class="muted">for</span>
              <AppLink :to="`/${t.mondo_id}`">{{ t.disorder }}</AppLink>
            </template>
            <span v-if="t.modality" class="chip">{{
              enumLabel(t.modality)
            }}</span>
            <span v-if="t.action_category" class="chip">{{
              enumLabel(t.action_category)
            }}</span>
          </div>
          <div v-if="t.agents.length" class="agents">
            <span class="muted">Agents</span>
            <template v-for="a in t.agents" :key="a.id">
              <AppLink v-if="a.in_kg" :to="`/${a.id}`" class="chip">{{
                a.label || a.id
              }}</AppLink>
              <span v-else class="chip">{{ a.label || a.id }}</span>
            </template>
          </div>
          <p v-if="t.description" class="description">{{ t.description }}</p>
          <ul v-if="t.target_mechanisms.length" class="targets">
            <li v-for="m in t.target_mechanisms" :key="m.node_id">
              <span class="effect">{{ enumLabel(m.effect) || "Targets" }}</span>
              <span
                v-tooltip="
                  m.resolved
                    ? {
                        content: nodeTooltip(data.mechanism_nodes, m.node_id),
                        allowHTML: true,
                        maxWidth: 360,
                        interactive: true,
                        appendTo: appendToBody,
                      }
                    : 'Not a mechanism recorded for this disorder'
                "
                :class="['mechanism', { unresolved: !m.resolved }]"
                >{{ m.name }}</span
              >
              <span v-if="m.description" class="muted">
                {{ m.description }}</span
              >
            </li>
          </ul>
          <div v-if="t.target_phenotypes.length" class="agents">
            <span class="muted">Treats</span>
            <AppLink
              v-for="p in t.target_phenotypes"
              :key="p.hpo_id"
              :to="`/${p.hpo_id}`"
              class="chip"
              >{{ p.label || p.hpo_id }}</AppLink
            >
          </div>
          <AppButton
            v-if="t.evidence.length"
            :text="`${expanded[t.treatment_node_id] ? 'Hide' : 'Show'} ${t.evidence.length} references`"
            design="small"
            color="secondary"
            @click="
              expanded[t.treatment_node_id] = !expanded[t.treatment_node_id]
            "
          />
          <ul v-if="expanded[t.treatment_node_id]" class="evidence">
            <li v-for="e in t.evidence" :key="e.reference + e.snippet">
              <AppLink
                v-if="e.reference.startsWith('PMID:')"
                :to="`https://pubmed.ncbi.nlm.nih.gov/${e.reference.slice(5)}`"
                >{{ e.reference }}</AppLink
              >
              <span v-else>{{ e.reference }}</span>
              <q v-if="e.snippet">{{ e.snippet }}</q>
            </li>
          </ul>
        </div>
        <div class="muted release">
          <AppLink
            v-if="byDisease && data.rows[0]"
            :to="dismechDisorderUrl(data.rows[0].disorder_file)"
            >View on Dismech</AppLink
          >
          Dismech release {{ data.release }}
        </div>
      </div>
    </template>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { getDismechTreatments } from "@/api/dismech";
import type { DismechTreatments } from "@/api/dismech";
import type { Node } from "@/api/model";
import AppAlert from "@/components/AppAlert.vue";
import { useQuery } from "@/composables/use-query";
import { useResearchUseAcknowledgement } from "@/composables/use-research-use-acknowledgement";
import { appendToBody } from "@/global/tooltip";
import {
  dismechDisorderUrl,
  enumLabel,
  nodeTooltip,
  useDismechPreview,
} from "@/util/dismech";

type Props = {
  node: Node;
};

const props = defineProps<Props>();

const preview = useDismechPreview();
const { acknowledged, acknowledge } = useResearchUseAcknowledgement();
const expanded = ref<Record<string, boolean>>({});

const byDisease = computed(() => props.node.category === "biolink:Disease");
const isDrug = computed(() => /^(CHEBI|NCIT):/.test(props.node.id));
const show = computed(() => preview.value && (byDisease.value || isDrug.value));
const heading = computed(() =>
  byDisease.value
    ? "Treatments and the mechanisms they target"
    : "Diseases treated, and the mechanisms targeted",
);

const { query, data, isLoading, isError } = useQuery(
  async () => await getDismechTreatments(props.node.id),
  { id: "", release: "", rows: [], mechanism_nodes: {} } as DismechTreatments,
);

/** nothing is fetched until the research-use notice is acknowledged */
watch(
  () => [props.node.id, show.value, acknowledged.value],
  () => {
    expanded.value = {};
    if (show.value && acknowledged.value) query();
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.notice {
  width: 100%;
}

.treatments {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 20px;
}

.treatment {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-bottom: 20px;
  gap: 8px;
  border-bottom: solid 1px $light-gray;
}

.title,
.agents {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.description {
  margin: 0;
}

.chip {
  padding: 1px 8px;
  border-radius: 999px;
  background: $light-gray;
  font-size: 0.85em;
}

.targets {
  margin: 0;
  padding-left: 20px;
}

.effect {
  margin-right: 6px;
  font-weight: 600;
}

.mechanism {
  padding: 1px 6px;
  border: solid 1px $theme;
  border-radius: 4px;
  cursor: help;
}

.mechanism.unresolved {
  border-style: dashed;
}

.muted {
  color: $dark-gray;
  font-size: 0.9em;
}

.ai {
  color: $theme;
}

.evidence {
  margin: 0;
  padding-left: 20px;

  q {
    margin-left: 6px;
    color: $dark-gray;
    font-style: italic;
  }
}

.release {
  display: flex;
  align-self: flex-end;
  gap: 15px;
}
</style>
