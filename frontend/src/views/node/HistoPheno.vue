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
import { computed, watch } from "vue";
import { useRoute } from "vue-router";
import Apex from "vue3-apexcharts";
import { getHistoPheno } from "@/api/histopheno";
import type { Node } from "@/api/model";
import { useQuery } from "@/util/composables";
import { ensure } from "@/util/object";

// import theme from "@/global/variables.module.scss";

/** route info */
const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** chart options */
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

/** get chart data */
const {
  query: getData,
  data: series,
  isLoading,
  isError,
} = useQuery(
  async function () {
    console.log(`Getting HistoPheno for ${props.node}`);
    const node_id = ensure(props.node.id);
    const histopheno = await getHistoPheno(ensure(node_id));
    const data = histopheno.items?.map((d) => ({ x: d.label, y: d.count }));

    return [{ name: "phenotypes", data: data }];
  },

  /** default value */
  []
);

/** when path (not hash or query) changed, get new chart data */
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
