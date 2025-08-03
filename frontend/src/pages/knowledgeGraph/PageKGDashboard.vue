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
        <DataSource
          name="gene_connection_report"
          url="qc/gene_connection_report.tsv"
          description="Gene ortholog and phenotype connection analysis"
          format="csv"
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

        <!-- Charts Section -->
        <div class="dashboard-section">
          <h3>Data Visualizations</h3>
          
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

      <!-- Future Visualizations Section -->
      <div class="charts-section">
        <h3>Future Visualizations</h3>
        <div class="charts-grid">
          <!-- Placeholder for Time Series Chart -->
          <div class="chart-placeholder">
            <h4>Data Growth Over Time</h4>
            <div class="placeholder-content">
              <AppIcon icon="trending-up" />
              <p>Time Series Chart</p>
              <p class="placeholder-desc">
                Coming Soon: Track KG growth and updates over time
              </p>
            </div>
          </div>
          
          <!-- Placeholder for Network Graph -->
          <div class="chart-placeholder">
            <h4>Interactive Network Graph</h4>
            <div class="placeholder-content">
              <AppIcon icon="share-2" />
              <p>Network Visualization</p>
              <p class="placeholder-desc">
                Coming Soon: Explore entity relationships interactively
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
import SankeyChart from "@/components/dashboard/SankeyChart.vue";
import ChordChart from "@/components/dashboard/ChordChart.vue";
import BarChart from "@/components/dashboard/BarChart.vue";
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
    background-color: #f8faff;
    color: #374151;
    font-size: 0.95rem;
    line-height: 1.6;
    border-radius: 0 6px 6px 0;
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
