<template>
  <!-- status -->
  <AppStatus v-if="isLoading" code="loading">Loading histopheno data</AppStatus>
  <AppStatus v-else-if="isError" code="error"
    >Error loading histopheno data</AppStatus
  >

  <!-- results -->
  <Apex
    v-if="series[0]?.data?.length"
    type="bar"
    :options="options"
    :series="series"
  />

  <div v-else>No info</div>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute } from "vue-router";
/** https://apexcharts.com/docs/vue-charts/ */
import Apex from "vue3-apexcharts";
import type { ApexOptions } from "apexcharts";
import { getHistoPheno } from "@/api/histopheno";
import type { Node } from "@/api/model";
import { useQuery } from "@/util/use-query";

/** route info */
const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** chart options */
const options = computed<ApexOptions>(() => ({
  chart: {
    id: "histopheno",
    type: "bar",
    redrawOnParentResize: true,
  },
  title: {
    text: `Breakdown of phenotypes associated with ${props.node.name}`,
  },
  colors: ["#00acc1"],
  plotOptions: {
    bar: {
      horizontal: true,
    },
  },
  tooltip: {
    enabled: false,
  },
  xaxis: {
    title: {
      text: "# of Phenotypes",
    },
    axisBorder: {
      color: "#000000",
    },
    axisTicks: {
      show: true,
      color: "#000000",
    },
  },
  yaxis: {},
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

/** get chart data */
const {
  query: runGetHistoPheno,
  data: series,
  isLoading,
  isError,
} = useQuery(
  async function () {
    const histopheno = await getHistoPheno(props.node.id || "");
    const data = histopheno.items
      ?.map((d) => ({ x: d.label, y: d.count }))
      ?.filter((d) => d.y);
    return [{ name: "phenotypes", data: data }];
  },

  /** default value */
  [],
);

/** when path (not hash or query) changed, get new chart data */
watch([() => route.path, () => props.node.id], runGetHistoPheno, {
  immediate: true,
});
</script>
