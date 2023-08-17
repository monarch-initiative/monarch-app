<!--
  about publications page

  list of publication and other works related to monarch, sorted by year
-->

<template>
  <AppHeading>Publications</AppHeading>

  <AppSection>
    <AppFlex direction="row" gap="big" align-v="top">
      <!-- citation count metadata as apex chart -->
      <Apex type="bar" :options="options" :series="cites_per_year" />
      <ul id="section_citations" align-h="right">
        <li v-for="item in metadata_table" :key="item">
          {{ item.key }}: {{ item.value }}
        </li>
      </ul>
    </AppFlex>
  </AppSection>

  <AppSection>
    <AppHeading>Publications by Year</AppHeading>
    <!-- row of links to year sections -->
    <p>
      <template
        v-for="(group, index) in publications.publications"
        :key="index"
      >
        <AppLink :to="'#' + group.year">{{ group.year }}</AppLink>
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
    <AppHeading>{{ group.year }}</AppHeading>
    <AppGallery size="big">
      <AppCitation
        v-for="(publication, item) in group.items"
        :key="item"
        :title="publication.title"
        :authors="publication.authors"
        :details="[publication.journal, publication.issue, publication.link]"
      />
    </AppGallery>
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from "vue";
import Apex from "vue3-apexcharts";
import AppCitation from "@/components/AppCitation.vue";
import publications from "./publications.json";

const metadata = computed(() => publications.metadata);

/** Make list of citations by year for apex chart */
const cites_per_year = computed(() => {
  const cites_per_year = [];
  for (const [year, count] of Object.entries(metadata.value.cites_per_year)) {
    cites_per_year.push({ x: year, y: count });
  }
  return [{ name: "citations", data: cites_per_year }];
});

const metadata_table = computed(() => {
  // const metadata_table = [];
  const metadata_table = [
    { key: "Monarch Publications", value: metadata.value.num_publications },
    { key: "Total Citations", value: metadata.value.total },
    { key: "Last 5 Years", value: metadata.value.last_5_yrs },
  ];
  // for (const [key, value] of Object.entries(metadata.value)) {
  //   if (key === "cites_per_year") continue;
  //   metadata_table.push({ key: key, value: value });
  // }
  return metadata_table;
});

/** chart options */
const options = computed(() => ({
  chart: {
    id: "citations",
    type: "histograph",
    redrawOnParentResize: true,
    width: "100%",
    height: "100%",
  },
  title: {
    text: `Monarch Citations`,
  },
  colors: ["#00acc1"],
  plotOptions: {
    bar: {
      // horizontal: true,
      horizontal: false,
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
}));
</script>

<style scoped lang="scss">
// #section_citations {
//   width: 25%;
// }
.vue-apexcharts {
  width: 65%;
}
.apexcharts-menu-item {
  white-space: nowrap;
}
</style>
