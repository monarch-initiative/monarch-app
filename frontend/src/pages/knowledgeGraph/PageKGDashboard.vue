<template>
  <div class="kg-dashboard">
    <AppBreadcrumb />
    <PageTitle id="kg-dashboard" title="KG Dashboard" />

    <!-- Dashboard Content -->
    <AppSection width="big">
      <p class="content">
        Explore the Monarch Knowledge Graph through interactive data
        visualizations. This dashboard provides insights into graph structure,
        data quality, and content statistics using live parquet data from the KG
        source.
      </p>

      <!-- KG Dashboard with Data Sources -->
      <KGDashboard>
        <!-- Declare parquet data sources from KG QC directory -->
        <DataSource
          name="node_report"
          url="qc/node_report.parquet"
          description="Node statistics and categories from KG quality control"
        />
        <DataSource
          name="edge_report"
          url="qc/edge_report.parquet"
          description="Edge/association statistics from KG quality control"
        />

        <!-- Knowledge Graph Metrics -->
        <div class="dashboard-section">
          <h3>Knowledge Graph Overview</h3>

          <div class="metrics-grid">
            <KGMetricCard
              title="Total Nodes"
              data-source="node_report"
              sql="SELECT SUM(count) as total_nodes FROM node_report"
              subtitle="entities in graph"
              description="Total number of biomedical entities in the knowledge graph"
            />

            <KGMetricCard
              title="Total Associations"
              data-source="edge_report"
              sql="SELECT SUM(count) as total_edges FROM edge_report"
              subtitle="relationships"
              description="Number of semantic relationships between entities"
            />
          </div>
        </div>

        <!-- Core Entity Metrics -->
        <div class="dashboard-section">
          <h3>Core Entities</h3>

          <div class="metrics-grid">
            <KGMetricCard
              title="Genes"
              data-source="node_report"
              sql="SELECT SUM(count) as genes FROM node_report WHERE category = 'biolink:Gene'"
              description="Number of gene entities in the knowledge graph"
            />

            <KGMetricCard
              title="Diseases"
              data-source="node_report"
              sql="SELECT SUM(count) as diseases FROM node_report WHERE category = 'biolink:Disease'"
              description="Total disease entities"
            />

            <KGMetricCard
              title="Phenotypes"
              data-source="node_report"
              sql="SELECT SUM(count) as phenotypes FROM node_report WHERE category = 'biolink:PhenotypicFeature'"
              description="Total number of phenotype entities in the knowledge graph"
            />
          </div>
        </div>

        <!-- Charts Section -->
        <div class="dashboard-section">
          <h3>Data Visualizations</h3>

          <!-- Chord Chart - Category Connections -->
          <ChordChart
            title="Knowledge Graph Category Connections"
            data-source="edge_report"
            sql="
              SELECT
              replace(subject_category, 'biolink:', '') as subject_category,
              replace(object_category, 'biolink:', '') as object_category,
              SUM(count) as count
              FROM edge_report
              GROUP BY all
              HAVING count > 1000
              ORDER BY count DESC

            "
            :show-controls="true"
            :allow-export="true"
            height="600px"
          />

          <!-- Sankey Chart - Knowledge Flow -->
          <SankeyChart
            title="Knowledge Graph Flow"
            data-source="edge_report"
            sql="
              SELECT
              replace(subject_category, 'biolink:', '') as subject_category,
              replace(predicate, 'biolink:', '') as predicate,
              replace(object_category, 'biolink:', '') || ' ' as object_category,
              SUM(count) as count
              FROM edge_report
              GROUP BY subject_category, predicate, object_category
              ORDER BY count DESC
              LIMIT 50
            "
            :show-controls="true"
            :allow-export="true"
            height="800px"
          />

          <!-- Bar Chart - Node Distribution by Category -->
          <BarChart
            title="Node Distribution by Category"
            data-source="node_report"
            sql="
              SELECT
              replace(category, 'biolink:', '') as category,
              SUM(count) as count
              FROM node_report
              WHERE category IS NOT NULL
              GROUP BY category
              ORDER BY count DESC
              LIMIT 15
            "
            :show-controls="true"
            :allow-export="true"
            orientation="horizontal"
            height="600px"
          />
        </div>
      </KGDashboard>
    </AppSection>
  </div>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import BarChart from "@/components/dashboard/BarChart.vue";
import ChordChart from "@/components/dashboard/ChordChart.vue";
import DataSource from "@/components/dashboard/DataSource.vue";
import KGDashboard from "@/components/dashboard/KGDashboard.vue";
import KGMetricCard from "@/components/dashboard/KGMetricCard.vue";
import SankeyChart from "@/components/dashboard/SankeyChart.vue";
import PageTitle from "@/components/ThePageTitle.vue";
</script>

<style lang="scss" scoped>
.kg-dashboard {
  min-height: 100vh;
}

.content {
  margin-bottom: 2rem;
  color: #4b5563;
  font-size: 1rem;
  text-align: left;
}

.dashboard-section {
  margin: 2rem 0;

  h3 {
    margin: 0 0 1.5rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e5e7eb;
    color: #374151;
    font-weight: 600;
    font-size: 1.25rem;
  }

  .section-description {
    margin: 0 0 2rem 0;
    padding: 1rem 1.5rem;
    border-left: 4px solid #3b82f6;
    border-radius: 0 6px 6px 0;
    background-color: #f8faff;
    color: #374151;
    font-size: 0.95rem;
    line-height: 1.6;
  }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  margin: 2rem 0;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>
