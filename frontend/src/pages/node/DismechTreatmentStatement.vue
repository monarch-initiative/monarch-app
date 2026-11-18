<!--
  a dismech treatment as one statement in a drug section, styled like the
  section's own statements; it expands to the dismech record behind it
-->

<template>
  <li class="statement">
    <!-- mouse convenience; the expand button is the keyboard control -->
    <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events, vuejs-accessibility/no-static-element-interactions -->
    <div class="statement-row" @click="open = !open">
      <button
        class="expand"
        :aria-expanded="open"
        :aria-label="`Dismech record for ${treatment.name}`"
        @click.stop="open = !open"
      >
        <AppIcon :icon="open ? 'angle-down' : 'angle-right'" />
      </button>
      <span class="predicate">{{ predicate }}</span>
      <span v-if="!showDisease || !treatment.mondo_id" class="target">{{
        showDisease ? treatment.disorder : diseaseName
      }}</span>
      <span v-else class="target" @click.stop>
        <AppNodeBadge
          :node="{
            id: treatment.mondo_id,
            name: treatment.disorder,
            category: 'biolink:Disease',
          }"
        />
      </span>
      <span class="context">as {{ treatment.name }}</span>
      <span class="where">
        <span
          v-tooltip="'Dismech: AI-assisted curation, may have mistakes'"
          class="pill dismech"
          ><AppIcon icon="robot" /> Dismech</span
        >
      </span>
    </div>
    <div v-if="open" class="assertions">
      <DismechTreatmentDetail
        :treatment="treatment"
        :nodes="nodes"
        :release="release"
        :monarch-row="monarchRow"
      />
    </div>
  </li>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { DismechTreatment, MechanismNode } from "@/api/dismech";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import DismechTreatmentDetail from "@/pages/node/DismechTreatmentDetail.vue";

type Props = {
  treatment: DismechTreatment;
  nodes: Record<string, MechanismNode>;
  release: string;
  /** the section's word for the relationship, e.g. "treats" */
  predicate: string;
  /** link the disease (drug page); else name the page's disease */
  showDisease?: boolean;
  /** the page's disease, on a disease page */
  diseaseName?: string;
  /** the section row the treatment is matched to, if any */
  monarchRow?: string;
};

defineProps<Props>();

const open = ref(false);
</script>

<style lang="scss" scoped>
/* matches the drug section's own statement rows */
.statement {
  padding: 4px 0;
}

.statement-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  width: 100%;
  padding: 4px 0;
  gap: 8px;
  cursor: pointer;

  &:hover {
    background: $off-white;
  }
}

.expand {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  border-radius: $rounded;
  background: none;
  color: inherit;
  cursor: pointer;

  &:focus-visible {
    outline: none;
    box-shadow: $outline;
  }
}

.predicate {
  color: $theme;
  font-weight: 600;
}

.context {
  padding: 1px 6px;
  border-radius: $rounded;
  background: $theme-light;
  font-size: 0.8rem;
}

.where {
  display: flex;
  margin-left: auto;
  gap: 4px;
}

.pill {
  padding: 1px 6px;
  border-radius: $rounded;
  background: $light-gray;
  font-size: 0.8rem;
  white-space: nowrap;
}

.pill.dismech {
  color: $theme;
}

.assertions {
  display: flex;
  flex-direction: column;
  margin: 6px 0 6px 24px;
  gap: 10px;
}
</style>
