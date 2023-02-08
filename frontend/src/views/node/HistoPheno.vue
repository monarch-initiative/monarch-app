<template>
  <!-- status -->
  <AppStatus v-if="isLoading" code="loading"
    >Loading histo-pheno data</AppStatus
  >
  <AppStatus v-else-if="isError" code="error"
    >Error loading histo-pheno data</AppStatus
  >

  <!-- results -->
  <Apex v-if="series.length" type="bar" :options="options" :series="series" />
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import Apex from "vue3-apexcharts";
import { getHistoPheno } from "@/api/histo-pheno";
import { Node } from "@/api/node-lookup";
import { useQuery } from "@/util/composables";
import { computed, watch } from "vue";
import theme from "@/global/variables.module.scss";

/** route info */
const route = useRoute();

interface Props {
  /** current node */
  node: Node;
}

const props = defineProps<Props>();

/** chart options */
const options = computed(() => ({
  chart: {
    id: "histo-pheno",
    type: "bar",
    redrawOnParentResize: true,
    width: "100%",
    height: "100%",
  },
  title: {
    text: `Breakdown of phenotypes associated with ${props.node.name}`,
  },
  colors: [theme.theme],
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
    const data = await getHistoPheno(props.node.id);

    return [
      {
        name: "phenotypes",
        data: data.map((d) => ({ x: d.name, y: d.count })),
      },
    ];
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
