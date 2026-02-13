<template>
  <div :class="['predicate-detail-panel', { compact }]">
    <div v-if="!selectedPredicate" class="empty-state">
      <div class="empty-icon">
        <AppIcon icon="chart-bar" />
      </div>
      <h3>Select a Predicate</h3>
      <p>Click on a predicate in the bar chart to view detailed information</p>
    </div>

    <div v-else class="detail-content">
      <!-- Biolink Definition Section -->
      <div class="detail-section">
        <div v-if="biolinkLoading" class="definition-line">
          <h4 class="section-title-inline">
            <AppIcon icon="book" class="section-icon" />
            Biolink Definition
          </h4>
          <div class="loading-state-inline">
            <div class="spinner"></div>
            <span>Loading biolink model...</span>
          </div>
        </div>
        <div v-else-if="biolinkError" class="definition-line">
          <h4 class="section-title-inline">
            <AppIcon icon="book" class="section-icon" />
            Biolink Definition
          </h4>
          <div class="error-state-inline">
            <AppIcon icon="circle-exclamation" />
            <span>{{ biolinkError }}</span>
          </div>
        </div>
        <div v-else-if="predicateInfo" class="definition-container">
          <div class="definition-line">
            <h4 class="section-title-inline">
              <AppIcon icon="book" class="section-icon" />
              Biolink Definition
            </h4>
            <span class="definition-text">{{
              predicateInfo.description || "No description available"
            }}</span>
          </div>
          <button
            v-if="hasAdditionalInfo"
            class="show-more-button"
            @click="showMoreDetails = !showMoreDetails"
          >
            <AppIcon
              :icon="showMoreDetails ? 'chevron-up' : 'chevron-down'"
              class="chevron-icon"
            />
            {{
              showMoreDetails
                ? "Hide schema details"
                : "Show more schema details"
            }}
          </button>
          <dl v-if="showMoreDetails" class="schema-details">
            <template v-if="predicateInfo.domain">
              <dt>DOMAIN:</dt>
              <dd>{{ predicateInfo.domain }}</dd>
            </template>

            <template v-if="predicateInfo.range">
              <dt>RANGE:</dt>
              <dd>{{ predicateInfo.range }}</dd>
            </template>

            <template v-if="hasMappings">
              <dt>MAPPINGS</dt>
              <dd>
                <dl class="mappings-list">
                  <template v-if="predicateInfo.exact_mappings?.length">
                    <dt>Exact:</dt>
                    <dd>{{ predicateInfo.exact_mappings.join(", ") }}</dd>
                  </template>

                  <template v-if="predicateInfo.broad_mappings?.length">
                    <dt>Broad:</dt>
                    <dd>{{ predicateInfo.broad_mappings.join(", ") }}</dd>
                  </template>

                  <template v-if="predicateInfo.narrow_mappings?.length">
                    <dt>Narrow:</dt>
                    <dd>{{ predicateInfo.narrow_mappings.join(", ") }}</dd>
                  </template>

                  <template v-if="predicateInfo.related_mappings?.length">
                    <dt>Related:</dt>
                    <dd>{{ predicateInfo.related_mappings.join(", ") }}</dd>
                  </template>
                </dl>
              </dd>
            </template>
          </dl>
        </div>
        <div v-else class="definition-line">
          <h4 class="section-title-inline">
            <AppIcon icon="book" class="section-icon" />
            Biolink Definition
          </h4>
          <span class="info-state-inline">
            <AppIcon icon="circle-info" />
            No biolink definition found for this predicate
          </span>
        </div>
      </div>

      <!-- Node Connection Visualization Section -->
      <div class="detail-section">
        <h4 class="section-title">
          <AppIcon icon="diagram-project" class="section-icon" />
          Edge Type Network
        </h4>
        <NetworkChart
          ref="connectionChartRef"
          :title="''"
          data-source="edge_report"
          :sql="connectionSQL"
          :predicate="selectedPredicate || ''"
          :height="'400px'"
          :show-controls="false"
          :allow-export="true"
          @data-changed="onChartDataChanged"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import { useBiolinkModel } from "@/composables/use-biolink-model";
import type { PredicateInfo } from "@/composables/use-biolink-model";
import NetworkChart from "./NetworkChart.vue";

export interface Props {
  selectedPredicate: string | null;
  predicateCount: number;
  compact?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  selectedPredicate: null,
  predicateCount: 0,
  compact: false,
});

const connectionChartRef = ref<InstanceType<typeof NetworkChart>>();
const predicateInfo = ref<PredicateInfo | null>(null);
const showMoreDetails = ref(false);

// Biolink model composable
const {
  isLoading: biolinkLoading,
  error: biolinkError,
  loadBiolinkModel,
  getPredicateInfo,
} = useBiolinkModel();

/** Check if predicate has additional info beyond description */
const hasAdditionalInfo = computed(() => {
  if (!predicateInfo.value) return false;
  return !!(
    predicateInfo.value.domain ||
    predicateInfo.value.range ||
    hasMappings.value
  );
});

/** Check if predicate has any mappings */
const hasMappings = computed(() => {
  if (!predicateInfo.value) return false;
  return !!(
    predicateInfo.value.exact_mappings?.length ||
    predicateInfo.value.broad_mappings?.length ||
    predicateInfo.value.narrow_mappings?.length ||
    predicateInfo.value.related_mappings?.length
  );
});

/** SQL query for subject-object connections for the selected predicate */
const connectionSQL = computed(() => {
  if (!props.selectedPredicate) return "";

  return `
    SELECT
      replace(subject_category, 'biolink:', '') as subject_category,
      replace(object_category, 'biolink:', '') as object_category,
      SUM(count) as count
    FROM edge_report
    WHERE replace(predicate, 'biolink:', '') = '${props.selectedPredicate}'
    GROUP BY subject_category, object_category
    ORDER BY count DESC
    LIMIT 30
  `;
});

/** Load predicate info from biolink model */
const loadPredicateInfo = async () => {
  if (!props.selectedPredicate) {
    predicateInfo.value = null;
    return;
  }

  // Get predicate info
  predicateInfo.value = getPredicateInfo(props.selectedPredicate);
};

/** Handle chart data changes */
const onChartDataChanged = (data: any[]) => {
  // Network chart data updated
  console.debug("Network chart loaded with", data.length, "edges");
};

// Watch for selected predicate changes
watch(
  () => props.selectedPredicate,
  () => {
    loadPredicateInfo();
    showMoreDetails.value = false; // Reset expansion state
  },
);

// Load biolink model on mount
onMounted(async () => {
  await loadBiolinkModel();
  if (props.selectedPredicate) {
    loadPredicateInfo();
  }
});
</script>

<style lang="scss" scoped>
.predicate-detail-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
  padding: 1.5rem;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;

  &.compact {
    min-height: auto;
    padding: 0;
    border: none;
    border-radius: 0;
    background: transparent;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  text-align: center;

  .empty-icon {
    margin-bottom: 1rem;
    color: #9ca3af;
    font-size: 3rem;
  }

  h3 {
    margin: 0 0 0.5rem 0;
    color: #374151;
    font-weight: 600;
    font-size: 1.25rem;
  }

  p {
    margin: 0;
    color: #6b7280;
    font-size: 0.95rem;
  }
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  .compact & {
    gap: 0.75rem;
  }
}

.detail-section {
  .section-title {
    display: flex;
    align-items: center;
    margin: 0 0 0.75rem 0;
    gap: 0.5rem;
    color: #1f2937;
    font-weight: 600;
    font-size: 1rem;

    .section-icon {
      color: #3b82f6;
    }
  }

  .section-title-inline {
    display: flex;
    align-items: center;
    margin: 0;
    gap: 0.5rem;
    color: #1f2937;
    font-weight: 600;
    font-size: 0.95rem;
    white-space: nowrap;

    .section-icon {
      color: #3b82f6;
    }
  }
}

.definition-container {
  display: block;
  width: 100%;
}

.definition-line {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  line-height: 1.5;
}

.definition-text {
  flex: 1;
  color: #374151;
  font-size: 0.9rem;
}

.show-more-button {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  gap: 0.25rem;
  border: none;
  background: transparent;
  color: #3b82f6;
  font-weight: 500;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: #2563eb;
    text-decoration: underline;
  }

  .chevron-icon {
    font-size: 0.75rem;
  }
}

.schema-details {
  display: block;
  width: 100%;
  margin: 0.75rem 0 0 0;
  padding: 0.75rem;
  border-left: 3px solid #3b82f6;
  border-radius: 4px;
  background: #f9fafb;

  dt {
    margin: 0.75rem 0 0.25rem 0;
    color: #6b7280;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
    text-align: left;

    &:first-child {
      margin-top: 0;
    }
  }

  dd {
    margin: 0 0 0 1.5rem;
    padding: 0;
    color: #374151;
    font-size: 0.85rem;
    font-family: "Courier New", monospace;
    text-align: left;
  }

  .mappings-list {
    display: block;
    margin-top: 0.25rem;

    dt {
      margin: 0.5rem 0 0.25rem 0;
      color: #6b7280;
      font-weight: 500;
      font-size: 0.85rem;
      text-align: left;

      &:first-child {
        margin-top: 0;
      }
    }

    dd {
      margin: 0 0 0 1.5rem;
      padding: 0;
      color: #374151;
      font-size: 0.85rem;
      font-family: "Courier New", monospace;
      text-align: left;
      word-break: break-word;
    }
  }
}

.loading-state-inline,
.error-state-inline,
.info-state-inline {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.loading-state-inline {
  color: #0369a1;

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid #bae6fd;
    border-radius: 50%;
    border-top-color: #0369a1;
    animation: spin 0.8s linear infinite;
  }
}

.error-state-inline {
  color: #dc2626;
}

.info-state-inline {
  color: #d97706;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .predicate-detail-panel {
    padding: 1rem;
  }

  .section-title {
    font-size: 1rem;
  }
}
</style>
