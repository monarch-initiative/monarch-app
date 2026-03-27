<template>
  <div class="source-charts">
    <!-- Error state: column not available yet -->
    <div v-if="columnMissing" class="info-message">
      <AppStatus code="warning">
        The edge report data does not yet include per-source breakdowns. Charts
        will be available after the next KG build. The association browser below
        is fully functional.
      </AppStatus>
    </div>

    <template v-else-if="tier">
      <!-- Metric cards -->
      <div class="metrics-grid">
        <KGMetricCard
          title="Total Associations"
          data-source="edge_report"
          :sql="`SELECT SUM(count) as total FROM edge_report WHERE primary_knowledge_source = '${safeInforesId}'`"
          subtitle="associations from this source"
        />
        <KGMetricCard
          title="Subject Categories"
          data-source="edge_report"
          :sql="`SELECT COUNT(DISTINCT subject_category) as total FROM edge_report WHERE primary_knowledge_source = '${safeInforesId}'`"
          subtitle="unique subject categories"
        />
        <KGMetricCard
          title="Object Categories"
          data-source="edge_report"
          :sql="`SELECT COUNT(DISTINCT object_category) as total FROM edge_report WHERE primary_knowledge_source = '${safeInforesId}'`"
          subtitle="unique object categories"
        />
        <KGMetricCard
          title="Predicates"
          data-source="edge_report"
          :sql="`SELECT COUNT(DISTINCT predicate) as total FROM edge_report WHERE primary_knowledge_source = '${safeInforesId}'`"
          subtitle="unique predicates"
        />
      </div>

      <!-- Chord chart - Category Connections (all tiers) -->
      <div class="dashboard-section">
        <ChordChart
          :title="`${sourceName} — Category Connections`"
          data-source="edge_report"
          :sql="chordSql"
          :show-controls="true"
          :allow-export="true"
          height="600px"
        />
      </div>

      <!-- Ingest sources (provided_by) -->
      <div v-if="providedBySources.length" class="dashboard-section">
        <h3>Ingest Sources</h3>
        <div class="provided-by-tags">
          <span
            v-for="src in providedBySources"
            :key="src.name"
            class="provided-by-tag"
          >
            {{ src.name }} ({{ src.count.toLocaleString() }})
          </span>
        </div>
      </div>

      <!-- Predicate table (all tiers) -->
      <div class="dashboard-section">
        <h3>{{ sourceName }} — Predicate Analysis</h3>
        <PredicateTable
          data-source="edge_report"
          :sql="predicateTableSql"
          @predicate-selected="onPredicateSelected"
        />
      </div>

      <!-- Sankey chart (complex tier only) -->
      <div v-if="tier === 'complex'" class="dashboard-section">
        <SankeyChart
          :title="`${sourceName} — Knowledge Flow (Top 50 Edge Type Combinations)`"
          data-source="edge_report"
          :sql="sankeySql"
          :show-controls="true"
          :allow-export="true"
          height="800px"
        />
      </div>
    </template>

    <!-- Loading state for complexity probe -->
    <AppStatus v-else-if="probing" code="loading">
      Analyzing source data complexity...
    </AppStatus>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue";
import AppStatus from "@/components/AppStatus.vue";
import ChordChart from "@/components/dashboard/ChordChart.vue";
import KGMetricCard from "@/components/dashboard/KGMetricCard.vue";
import PredicateTable from "@/components/dashboard/PredicateTable.vue";
import SankeyChart from "@/components/dashboard/SankeyChart.vue";

type Props = {
  inforesId: string;
  sourceName: string;
};

const props = defineProps<Props>();

const emit = defineEmits<{
  "filter-predicate": [string];
  "filter-category": [string, "subjectCategory" | "objectCategory"];
}>();

/**
 * Sanitize inforesId for use in SQL WHERE clauses (alphanumeric, colons,
 * hyphens, underscores only)
 */
const safeInforesId = computed(() =>
  props.inforesId.replace(/[^a-zA-Z0-9:_-]/g, ""),
);

type Tier = "simple" | "moderate" | "complex";

const tier = ref<Tier | null>(null);
const probing = ref(true);
const columnMissing = ref(false);
const providedBySources = ref<{ name: string; count: number }[]>([]);

/** Get the kg-data provider from KGDashboard */
const kgData = inject<{
  executeQuery: (
    sql: string,
    sources?: string[],
  ) => Promise<Record<string, unknown>[]>;
}>("kg-data");

/** Run complexity probe to determine visualization tier */
const runProbe = async () => {
  if (!kgData) {
    probing.value = false;
    return;
  }
  try {
    const result = await kgData.executeQuery(
      `SELECT
        COUNT(DISTINCT subject_category) as sc,
        COUNT(DISTINCT object_category) as oc,
        COUNT(DISTINCT predicate) as p
       FROM edge_report
       WHERE primary_knowledge_source = '${safeInforesId.value}'`,
      ["edge_report"],
    );
    if (result.length === 0) {
      tier.value = "simple";
      probing.value = false;
      return;
    }
    const sc = Number(result[0].sc) || 0;
    const oc = Number(result[0].oc) || 0;
    const p = Number(result[0].p) || 0;
    const totalCategories = sc + oc;

    if (totalCategories <= 4 && p <= 3) {
      tier.value = "simple";
    } else if (totalCategories <= 10 && p <= 10) {
      tier.value = "moderate";
    } else {
      tier.value = "complex";
    }

    // Fetch provided_by (ingest source) breakdown
    try {
      const pbResult = await kgData.executeQuery(
        `SELECT provided_by, SUM(count) as count
         FROM edge_report
         WHERE primary_knowledge_source = '${safeInforesId.value}'
         GROUP BY provided_by
         ORDER BY count DESC`,
        ["edge_report"],
      );
      providedBySources.value = pbResult.map((row) => ({
        name: String(row.provided_by ?? "unknown"),
        count: Number(row.count) || 0,
      }));
    } catch {
      // provided_by column may not exist yet — silently skip
    }
  } catch (e) {
    const msg = String(e);
    if (
      msg.includes("primary_knowledge_source") &&
      (msg.includes("not found") ||
        msg.includes("Referenced column") ||
        msg.includes("Binder Error"))
    ) {
      columnMissing.value = true;
    } else {
      console.error("Probe query failed:", e);
      columnMissing.value = true;
    }
  } finally {
    probing.value = false;
  }
};

onMounted(() => {
  runProbe();
});

/** SQL queries for each chart type, filtered by source */
const whereClause = computed(
  () => `WHERE primary_knowledge_source = '${safeInforesId.value}'`,
);

const predicateTableSql = computed(
  () => `
    SELECT
      replace(predicate, 'biolink:', '') as category,
      SUM(count) as count
    FROM edge_report
    ${whereClause.value}
      AND predicate IS NOT NULL
    GROUP BY predicate
    ORDER BY count DESC
  `,
);

const chordSql = computed(
  () => `
    SELECT
      replace(subject_category, 'biolink:', '') as subject_category,
      replace(object_category, 'biolink:', '') as object_category,
      SUM(count) as count
    FROM edge_report
    ${whereClause.value}
    GROUP BY all
    ORDER BY count DESC
  `,
);

const sankeySql = computed(
  () => `
    SELECT
      replace(subject_category, 'biolink:', '') as subject_category,
      replace(predicate, 'biolink:', '') as predicate,
      replace(object_category, 'biolink:', '') || ' ' as object_category,
      SUM(count) as count
    FROM edge_report
    ${whereClause.value}
    GROUP BY subject_category, predicate, object_category
    ORDER BY count DESC
    LIMIT 50
  `,
);

/** Event handlers for chart-to-browser interaction */
const onPredicateSelected = (predicate: string) => {
  emit("filter-predicate", `biolink:${predicate}`);
};
</script>

<style lang="scss" scoped>
.source-charts {
  margin: 2rem 0;
}

.info-message {
  margin: 1rem 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  margin: 2rem 0;
  gap: 1.5rem;
}

.dashboard-section {
  margin: 2rem 0;

  h3 {
    margin: 0 0 1.5rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid $light-gray;
    color: $off-black;
    font-weight: 600;
    font-size: 1.25rem;
  }
}

.provided-by-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em;
}

.provided-by-tag {
  display: inline-block;
  padding: 0.35em 0.9em;
  border-radius: 999em;
  background-color: $light-gray;
  box-shadow: 0 0.07em 0.14em rgba(0, 0, 0, 0.04);
  font-weight: 500;
  font-size: 0.85em;
  transition: background-color $fast;

  &:hover {
    background-color: $theme-light;
  }
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>
