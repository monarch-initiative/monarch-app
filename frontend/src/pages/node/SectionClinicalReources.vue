<template>
  <AppDetail
    v-if="clinicalResources?.length"
    title="Patient and Clinical Resources"
    :full="true"
  >
    <div class="clinical-resources">
      <div class="custom-grid">
        <div v-for="(res, id) in clinicalResources" :key="id" class="linkout">
          <AppLink
            v-tooltip="res.tooltip"
            :to="res.url || ''"
            class="brand-chip"
            :style="chipStyle(res)"
            :aria-label="res.label || res.id"
          >
            <span>
              {{ brandText(res.id, res.label) }}
            </span>
            <small class="brand-id">{{ res.id }}</small>
          </AppLink>

          <!-- removed the bottom ID display -->
        </div>
      </div>

      <div class="sub-items">
        <div v-if="node?.inheritance">
          <span> Heritability : </span>
          <AppFlex align-h="left" gap="small">
            <AppLink
              v-tooltip="node?.inheritance?.name"
              :to="node?.inheritance?.id || ''"
              >{{ node?.inheritance?.name }}</AppLink
            >
          </AppFlex>
        </div>

        <div v-if="node?.causal_gene?.length">
          <span> Casual Genes : </span>
          <AppFlex align-h="left" gap="small">
            <AppNodeBadge
              v-for="(gene, index) in node?.causal_gene"
              :key="index"
              :node="omit(gene, 'in_taxon_label')"
            />
          </AppFlex>
        </div>

        <div>
          <span> Frequency : </span>
          <span>{{ frequencyLabel }}</span>
        </div>
      </div>
    </div>
  </AppDetail>
</template>

<script setup lang="ts">
import { computed, type ComputedRef } from "vue";
import omit from "lodash/omit";
import type { Entity, Node as ModelNode } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppLink from "@/components/AppLink.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { useClinicalResources } from "@/composables/use-clinical-resources";
import type { ClinicalResourceEntry } from "@/composables/use-clinical-resources";
import { BRAND_STYLES, brandFromId } from "@/util/linkout";

type Props = {
  clinicalSynopsis?: { id: string; url?: string }[];
  infoForPatients?: { id: string; url?: string }[];
  frequencyLabel?: "Rare" | "Common";
  node: ModelNode;
};

const { node, frequencyLabel } = defineProps<Props>();
console.log("node in clinical resources", node);
const clinicalResources = useClinicalResources(node)
  .clinicalResources as ComputedRef<ClinicalResourceEntry[]>;
const chipStyle = (res: ClinicalResourceEntry) => {
  const k = brandFromId(res.id);
  const s = k ? BRAND_STYLES[k] : undefined;
  return {
    "--brand-bg": s?.bg ?? "#666",
    "--brand-hover": s?.hover ?? s?.bg ?? "#666",
    "--brand-fg": s?.fg ?? "#fff",
    "--brand-border": s?.border ?? "#444",
  } as Record<string, string>;
};

const brandText = (id: string, fallback?: string) => {
  const k = brandFromId(id);
  return k ? BRAND_STYLES[k].label : fallback || id.split(":")[0];
};
</script>

<style lang="scss" scoped>
.clinical-resources {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  padding: 1em;
  gap: 1.5em;
  border: 1px solid $light-gray;
  background-color: $light-blue;
}
.custom-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.25em;
}

.sub-items {
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  gap: 0.9em;
}

.linkout {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35em;
}

.brand-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1rem;
  gap: 0.15em;
  border-radius: 12px;
  background: var(--brand-bg);
  box-shadow: 0 16px 38px rgba(16, 24, 40, 0.12);
  color: var(--brand-fg);
  font-weight: 700;
  text-decoration: none;
  transition:
    background-color 120ms ease,
    transform 120ms ease,
    box-shadow 120ms ease;
}
.brand-chip:hover,
.brand-chip:focus {
  transform: translateY(-1px);
  background: var(--brand-hover);
  box-shadow: 0 6px 18px rgba(16, 24, 40, 0.12);
}

.brand-id {
  font-size: 0.7rem;
  line-height: 1;
  opacity: 0.75;
}
.causal-genes {
  display: inline-flex !important;
  flex-wrap: wrap; /* wrap to next line when needed */
  gap: 0.8em;
  vertical-align: middle;
}
</style>
