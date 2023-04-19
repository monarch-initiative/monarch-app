<template>
  <!-- status -->
  <AppStatus v-if="isLoading" code="loading">Loading histopheno data</AppStatus>
  <AppStatus v-else-if="isError" code="error"
    >Error loading histopheno data</AppStatus
  >

  <!-- results -->
  <Apex v-if="series.length" type="bar" :options="options" :series="series" />
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import Apex from "vue3-apexcharts";
import { getHistoPheno } from "@/api/histopheno";
import type { Node } from "@/api/node-lookup";
import { useQuery } from "@/util/composables";
import { computed, watch } from "vue";

/** Route info */
const route = useRoute();

type Props = {
  /** Current node */
  node: Node;
};

const props = defineProps<Props>();

/** Chart options */
const options = computed(() => ({
  chart: {
    id: "histopheno",
    type: "bar",
    redrawOnParentResize: true,
    width: "100%",
    height: "100%",
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

/** Get chart data */
const {
  query: getData,
  data: series,
  isLoading,
  isError,
} = useQuery(
  async function () {
    const histopheno = await getHistoPheno(props.node.id);
    const data = histopheno.items?.map((d) => ({ x: d.label, y: d.count }));

    return [{ name: "phenotypes", data: data }];
  },

  /** Default value */
  []
);

/** When path (not hash or query) changed, get new chart data */
watch([() => route.path, () => props.node.id], getData, { immediate: true });
</script>

<style lang="scss" scoped>
.vue-apexcharts {
  width: 100%;
}
</style>

<style>
.apexcharts-menu-item {
  white-space: nowrap;
}
</style>
