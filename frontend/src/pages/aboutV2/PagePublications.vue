<template>
  <AppBreadcrumb class="publications" />
  <PageTitle
    id="publications0"
    title="Monarch Publications"
    class="publications"
  />

  <!-- Top metadata section: short description + key metrics -->
  <AppSection width="big">
    <p class="metadata">
      The Monarch Initiative maintains a rich and foundational body of
      publications that trace back to its early days, underscoring how these
      works have been pivotal in shaping the fields of variant interpretation,
      knowledge graphs, and disease gene discovery. Committed to open science,
      Monarch shares much of this work as preprints or in open-access venues,
      ensuring broad, transparent, and lasting accessibility. Use this page to
      explore Monarch’s full body of publications.
    </p>

    <AppGallery>
      <p v-for="(item, index) in metadata" :key="index" class="metadata">
        <strong>{{ item.name }}</strong>
        <br />
        <span>{{ publications.metadata[item.key].toLocaleString() }}</span>
      </p>
    </AppGallery>
  </AppSection>

  <!-- Publications grouped by year with a simple tab UI -->
  <AppSection width="big">
    <AppHeading>Publications by Year </AppHeading>

    <div class="tab-container">
      <div class="tabs" role="tablist" aria-label="Publication years">
        <div
          v-for="year in years"
          :key="year"
          class="tab-item"
          :class="{ active: activeYear === year }"
        >
          <AppButton
            :text="year"
            color="none"
            :aria-selected="activeYear === year"
            role="tab"
            :class="{ active: activeYear === year }"
            @click="setActiveYear(year)"
          />
        </div>
      </div>

      <!-- Panel shows items for the currently active year -->
      <div
        class="citations"
        role="tabpanel"
        :aria-labelledby="`tab-${activeYear}`"
      >
        <AppGallery>
          <AppCitation
            v-for="(publication, idx) in currentGroup.items"
            :key="idx"
            :link="publication.link"
            :title="publication.title"
            :authors="publication.authors"
            :details="[publication.journal, publication.issue]"
          />
        </AppGallery>
      </div>
    </div>
  </AppSection>

  <!-- Citations bar chart (ApexCharts) -->
  <AppSection>
    <AppHeading>Yearly Citation Trend </AppHeading>
    <Apex
      class="chart"
      type="bar"
      :options="options"
      :series="[citesPerYear]"
      height="300px"
    />
  </AppSection>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import Apex from "vue3-apexcharts";
import ApexCharts from "apexcharts";
import type { ApexOptions } from "apexcharts";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppButton from "@/components/AppButton.vue";
import AppCitation from "@/components/AppCitation.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import publications from "@/data/publications.json";

/** ----- Publications groups & tabs ----- */
// Types inferred directly from JSON for safety and IntelliSense
type PublicationsData = typeof publications;
// Each group contains a year and its items
type PublicationGroup = PublicationsData["publications"][number];

// Array of year-grouped publications
const groups = publications.publications as PublicationGroup[];
// Tab labels as strings because we use them for comparisons/ids
const years = computed(() => groups.map((g) => String(g.year)));
// Default to the first year group (if present)
const activeYear = ref<string>(years.value[0] ?? "");

// Currently selected group for the panel; fall back to first group safely
const currentGroup = computed<PublicationGroup>(() => {
  return groups.find((g) => String(g.year) === activeYear.value) || groups[0];
});

/** ----- Chart series ----- */
// Convert the cites_per_year object into [{ x: year, y: count }, ...]
const citesPerYear = {
  name: "citations",
  data: Object.entries(publications.metadata.cites_per_year).map(
    ([year, count]) => ({ x: year, y: count }),
  ),
};

// Cards shown above the tabs (keys reference publications.metadata fields)
const metadata: {
  name: string;
  key: keyof (typeof publications)["metadata"];
}[] = [
  { name: "Total publications", key: "num_publications" },
  { name: "Total citations", key: "total" },
  { name: "Citations in last 5 years", key: "last_5_yrs" },
];

/** ----- Base chart options ----- */
const options: ApexOptions = {
  chart: {
    id: "citations",
    type: "bar",
    redrawOnParentResize: true, // keep chart responsive inside containers
  },
  title: {
    text: `Monarch Citations`,
  },
  colors: ["#00acc1"], // single series color
  plotOptions: {
    bar: {
      horizontal: false,
      dataLabels: {
        orientation: "vertical",
      },
    },
  },
  states: {
    active: {
      allowMultipleDataPointsSelection: false,
      filter: { type: "lighten", value: 0.15 },
    },
  },
  tooltip: {
    enabled: false, // declutter; rely on selection highlight
  },
  xaxis: {
    title: { text: "Year" },
    axisBorder: { color: "#000000" },
    axisTicks: { show: true, color: "#000000" },
  },
  yaxis: {
    title: { text: "# of Citations" },
    axisBorder: { color: "#000000" },
    axisTicks: { show: true, color: "#000000" },
  },
  grid: {
    xaxis: { lines: { show: false } },
    yaxis: { lines: { show: false } },
  },
};

/**
 * Update activeYear and mirror the selection on the bar chart for context. We
 * clear any previous selection and then select the data point at index
 * `dataPointIndex`.
 */
function setActiveYear(year: string) {
  activeYear.value = year;
  nextTick(() => {
    const dataPointIndex = citesPerYear.data.findIndex(
      (item) => String(item.x) === year,
    );
    if (dataPointIndex >= 0) {
      ApexCharts.exec("citations", "clearSelectedDataPoints");
      ApexCharts.exec(
        "citations",
        "toggleDataPointSelection",
        0,
        dataPointIndex,
      );
    }
  });
}

// Initialize selection on mount so the default tab and the chart match
onMounted(() => setActiveYear(activeYear.value));
</script>

<style scoped lang="scss">
.section.center {
  padding-bottom: 10px;
}

.metadata {
  text-align: left;
}
.publications {
  background-color: #ffffff;
}

.tab-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin: 0 auto;
  padding: 1rem;
  gap: 1.5em;
}

.tabs {
  display: flex;
  width: 100%;
  margin-bottom: 1rem;
  overflow-x: auto;
  gap: 0.3rem;
  border-bottom: 3px solid $theme;
  background-color: #fff;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.tab-item.active {
  border: 1px solid #ccc;
  border-bottom: 0;
  background-color: #008080;
  color: #fff;
}

/* Ensure AppButton text remains readable in active tab */
.tab-item.active :deep(.button) {
  color: #fff !important;
}

.tab-item:not(.active) {
  border: 1px solid transparent;
  border-bottom: 0;
  background-color: #f5f5f5;
}

:deep(.button) {
  width: 100%;
  border: none;
  background-color: transparent;
  font-weight: bold;
  cursor: pointer;
  &:hover,
  &:focus {
    outline: none !important;
    box-shadow: none !important;
  }
}

.citations {
  max-height: 32rem;
  overflow-x: hidden;
  overflow-y: auto;
  scrollbar-color: $theme;
  scrollbar-gutter: stable both-edges;
  scrollbar-width: thin;
}

/* Subtle dark-mode contrast for the custom scrollbar colors */
@media (prefers-color-scheme: dark) {
  .citations {
    scrollbar-color: rgba(0, 200, 200, 0.7) rgba(255, 255, 255, 0.08);
  }
}
</style>
