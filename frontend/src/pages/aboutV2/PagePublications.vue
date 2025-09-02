<template>
  <AppBreadcrumb class="publications" />
  <PageTitle
    id="publications0"
    title="Monarch Publications"
    class="publications"
  />

  <!-- Top metadata section -->
  <AppSection>
    <p class="metadata">
      This list includes papers by the Monarch Team that were foundational to
      the current Monarch work. The graph below shows the number of citations to
      Monarch papers over time.
    </p>

    <AppGallery>
      <p v-for="(item, index) in metadata" :key="index" class="metadata">
        <strong>{{ item.name }}</strong>
        <br />
        <span>{{ publications.metadata[item.key].toLocaleString() }}</span>
      </p>
    </AppGallery>
  </AppSection>

  <!-- Year Tabs using the same style as KG Sources page -->
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

      <!-- Current year's publications -->
      <div
        class="year-content"
        role="tabpanel"
        :aria-labelledby="`tab-${activeYear}`"
      >
        <!-- <AppHeading :id="'year-' + activeYear">{{ activeYear }}</AppHeading> -->
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

  <!-- Citations chart -->
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
/** https://apexcharts.com/docs/vue-charts/ */
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
// Types inferred from JSON shape
type PublicationsData = typeof publications;
type PublicationGroup = PublicationsData["publications"][number];

const groups = publications.publications as PublicationGroup[];
const years = computed(() => groups.map((g) => String(g.year)));
const activeYear = ref<string>(years.value[0] ?? ""); // default to first group

const currentGroup = computed<PublicationGroup>(() => {
  return groups.find((g) => String(g.year) === activeYear.value) || groups[0];
});

/** ----- Chart series ----- */
const citesPerYear = {
  name: "citations",
  data: Object.entries(publications.metadata.cites_per_year).map(
    ([year, count]) => ({ x: year, y: count }),
  ),
};

/** ----- Meta cards ----- */
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
    redrawOnParentResize: true,
  },
  title: {
    text: `Monarch Citations`,
  },
  colors: ["#00acc1"],
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
    enabled: false,
  },
  xaxis: {
    title: {
      text: "Year",
    },
    axisBorder: {
      color: "#000000",
    },
    axisTicks: {
      show: true,
      color: "#000000",
    },
  },
  yaxis: {
    title: {
      text: "# of Citations",
    },
    axisBorder: {
      color: "#000000",
    },
    axisTicks: {
      show: true,
      color: "#000000",
    },
  },
  grid: {
    xaxis: {
      lines: {
        show: false,
      },
    },
    yaxis: {
      lines: {
        show: false,
      },
    },
  },
};
function setActiveYear(year: string) {
  activeYear.value = year;
  nextTick(() => {
    const idx = citesPerYear.data.findIndex((p) => String(p.x) === year);
    if (idx >= 0) {
      ApexCharts.exec("citations", "clearSelectedDataPoints");
      ApexCharts.exec("citations", "toggleDataPointSelection", 0, idx);
    }
  });
}

onMounted(() => setActiveYear(activeYear.value));
</script>

<style scoped lang="scss">
.section.center {
  padding-bottom: 10px;
}
.section.big {
  gap: 20px;
}
.metadata {
  text-align: center;
}
.publications {
  background-color: #ffffff;
}

/* --- Reused tab styling (same as KG Sources page) --- */
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

.year-content {
  width: 100%;
}
</style>
