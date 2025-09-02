<template>
  <AppBreadcrumb class="publications" />
  <PageTitle
    id="publications0"
    title="Monarch Publications"
    class="publications"
  />
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

  <AppSection>
    <AppHeading>Years</AppHeading>
    <!-- row of links to year sections -->
    <p>
      <template
        v-for="(group, index) in publications.publications"
        :key="index"
      >
        <AppLink :to="'#year-' + group.year" :replace="true">
          {{ group.year }}</AppLink
        >
        <span v-if="index !== publications.publications.length - 1"> · </span>
      </template>
    </p>
  </AppSection>

  <!-- by year -->
  <AppSection
    v-for="(group, index) in publications.publications"
    :key="index"
    width="big"
  >
    <AppHeading :id="'year-' + group.year">{{ group.year }}</AppHeading>
    <AppGallery>
      <AppCitation
        v-for="(publication, item) in group.items"
        :key="item"
        :link="publication.link"
        :title="publication.title"
        :authors="publication.authors"
        :details="[publication.journal, publication.issue]"
      />
    </AppGallery>
  </AppSection>
  <AppSection>
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
import Apex from "vue3-apexcharts";
import type { ApexOptions } from "apexcharts";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppCitation from "@/components/AppCitation.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import publications from "@/data/publications.json";

/** data for chart */
const citesPerYear = {
  name: "citations",
  data: Object.entries(publications.metadata.cites_per_year).map(
    ([year, count]) => ({ x: year, y: count }),
  ),
};

/** extra metadata fields */
const metadata: {
  name: string;
  key: keyof (typeof publications)["metadata"];
}[] = [
  { name: "Total publications", key: "num_publications" },
  { name: "Total citations", key: "total" },
  { name: "Citations in last 5 years", key: "last_5_yrs" },
];

/** chart options */
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
</script>

<style scoped lang="scss">
.metadata {
  text-align: center;
}
.publications {
  background-color: #ffffff;
}
</style>
