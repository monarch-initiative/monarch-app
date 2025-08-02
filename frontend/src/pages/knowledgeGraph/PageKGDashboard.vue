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

            <KGMetricCard
              title="Unique Categories"
              data-source="node_report"
              sql="SELECT COUNT(DISTINCT category) as unique_categories FROM node_report WHERE category IS NOT NULL"
              subtitle="entity types"
              description="Number of distinct biomedical categories represented"
            />

          </div>
        </div>

        <!-- Data Distribution Metrics -->
        <div class="dashboard-section">
          <h3>Data Distribution</h3>

          <div class="metrics-grid">
            <KGMetricCard
              title="Human Genes"
              data-source="node_report"
              sql="SELECT SUM(count) as human_genes FROM node_report WHERE category = 'biolink:Gene' AND in_taxon = 'NCBITaxon:9606'"
              subtitle="Homo sapiens"
              description="Number of human gene entities in the knowledge graph"
            />

            <KGMetricCard
              title="Diseases"
              data-source="node_report"
              sql="SELECT SUM(count) as diseases FROM node_report WHERE category = 'biolink:Disease'"
              subtitle="conditions"
              description="Total disease entities"
            />

            <KGMetricCard
              title="Chemical Entities"
              data-source="node_report"
              sql="SELECT SUM(count) as chemicals FROM node_report WHERE category IN ('biolink:ChemicalEntity', 'biolink:Drug', 'biolink:SmallMolecule')"
              subtitle="compounds"
              description="Drugs, chemicals, and small molecule entities"
            />

            <KGMetricCard
              title="Gene-Disease Links"
              data-source="edge_report"
              sql="SELECT SUM(count) as gene_disease FROM edge_report WHERE subject_category = 'biolink:Gene' AND object_category = 'biolink:Disease'"
              subtitle="associations"
              description="Direct gene to disease association relationships"
            />
          </div>
        </div>
      </KGDashboard>

      <!-- Charts Section -->
      <div class="charts-section">
        <h3>Data Visualizations</h3>
        <div class="charts-grid">
          <!-- Placeholder for Bar Chart -->
          <div class="chart-placeholder">
            <h4>Node Distribution by Category</h4>
            <div class="placeholder-content">
              <AppIcon icon="bar-chart-2" />
              <p>Bar Chart Component</p>
              <p class="placeholder-desc">
                Coming Soon: Distribution of entities by biomedical category
              </p>
            </div>
          </div>

          <!-- Placeholder for Sankey Chart -->
          <div class="chart-placeholder">
            <h4>Knowledge Flow Diagram</h4>
            <div class="placeholder-content">
              <AppIcon icon="shuffle" />
              <p>Sankey Chart Component</p>
              <p class="placeholder-desc">
                Coming Soon: Data source → category → association flow
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Technical Info -->
      <div class="technical-info">
        <h3>Technical Implementation</h3>
        <div class="tech-grid">
          <div class="tech-item">
            <AppIcon icon="database" />
            <h4>DuckDB-WASM</h4>
            <p>Client-side analytics engine for processing parquet files</p>
          </div>
          <div class="tech-item">
            <AppIcon icon="activity" />
            <h4>Apache ECharts</h4>
            <p>Interactive charting library for data visualizations</p>
          </div>
          <div class="tech-item">
            <AppIcon icon="code" />
            <h4>SQL-Driven</h4>
            <p>Dashboard components powered by SQL queries against KG data</p>
          </div>
          <div class="tech-item">
            <AppIcon icon="zap" />
            <h4>Reactive</h4>
            <p>Vue 3 composables for real-time data updates and caching</p>
          </div>
        </div>
      </div>
    </AppSection>
  </div>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppIcon from "@/components/AppIcon.vue";
import AppSection from "@/components/AppSection.vue";
import DataSource from "@/components/dashboard/DataSource.vue";
import KGDashboard from "@/components/dashboard/KGDashboard.vue";
import KGMetricCard from "@/components/dashboard/KGMetricCard.vue";
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
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  margin: 2rem 0;
  gap: 1.5rem;
}

.charts-section {
  margin: 3rem 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  margin: 2rem 0;
  gap: 2rem;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 300px;
  padding: 2rem;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background: white;
  text-align: center;

  h4 {
    margin: 0 0 1rem 0;
    color: #374151;
    font-size: 1.125rem;
  }
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;

  .icon {
    margin-bottom: 0.5rem;
    font-size: 3rem;
  }

  p {
    margin: 0;

    &.placeholder-desc {
      max-width: 250px;
      color: #9ca3af;
      font-size: 0.875rem;
    }
  }
}

.technical-info {
  margin: 3rem 0;
  padding: 2rem;
  border-radius: 8px;
  background-color: #f9fafb;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  margin: 1.5rem 0;
  gap: 1.5rem;
}

.tech-item {
  padding: 1rem;
  text-align: center;

  .icon {
    margin-bottom: 0.5rem;
    color: #3b82f6;
    font-size: 2rem;
  }

  h4 {
    margin: 0.5rem 0;
    color: #1f2937;
    font-size: 1rem;
  }

  p {
    margin: 0;
    color: #6b7280;
    font-size: 0.875rem;
    line-height: 1.4;
  }
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .charts-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .tech-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .chart-placeholder {
    min-height: 250px;
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .tech-grid {
    grid-template-columns: 1fr;
  }
}
</style>
