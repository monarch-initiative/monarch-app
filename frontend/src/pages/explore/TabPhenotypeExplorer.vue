<!--
  phenotype explorer tab on explore page

  compare sets of phenotypes and genes/diseases
-->

<template>
  <AppSection>
    <!-- example -->
    <AppButton text="Try an example" design="small" @click="doExample()" />

    <strong>Compare these phenotypes ...</strong>

    <!-- set A -->
    <AppSelectTags
      ref="aBox"
      v-model="aPhenotypes"
      name="First set of phenotypes"
      :options="getPhenotypes"
      placeholder="Search for phenotypes, genes, or diseases"
      :tooltip="multiTooltip"
      :description="description(aPhenotypes, aGeneratedFrom)"
      @spread-options="(option, options) => spreadOptions(option, options, 'a')"
    />

    <!-- set B -->
    <AppFlex gap="small">
      <strong>... to</strong>
      <AppSelectSingle
        v-model="bMode"
        name="Second set mode"
        :options="bModeOptions"
      />
      <AppSelectSingle
        v-if="bMode.id.includes('genes')"
        v-model="bTaxon"
        name="Second set taxon"
        :options="bTaxonOptions"
      />
    </AppFlex>

    <AppSelectTags
      v-if="bMode.id.includes('these phenotypes')"
      v-model="bPhenotypes"
      name="Second set of phenotypes"
      :options="getPhenotypes"
      placeholder="Search for phenotypes, genes, or diseases"
      :tooltip="multiTooltip"
      :description="description(bPhenotypes, bGeneratedFrom)"
      @spread-options="(option, options) => spreadOptions(option, options, 'b')"
    />

    <!-- run analysis -->
    <AppButton
      v-if="bMode.id.includes('these phenotypes')"
      text="Analyze"
      icon="bars-progress"
      :disabled="isLoading || !aPhenotypes.length || !bPhenotypes.length"
      @click="runAnalysis"
    />
    <AppAlert v-else
      >This feature is still under development. Check back soon for
      more!</AppAlert
    >
  </AppSection>

  <AppSection v-if="comparison.summary.length || isLoading || isError">
    <AppHeading>Results</AppHeading>

    <p>Similarity comparison between pairs of phenotypes.</p>

    <!-- analysis status -->
    <AppStatus v-if="isLoading" code="loading">Running analysis</AppStatus>
    <AppStatus v-if="isError" code="error">Error running analysis</AppStatus>

    <!-- analysis top results -->
    <template v-else-if="comparison.summary.length">
      <!-- heading -->
      <AppHeading
        >Top {{ Math.min(comparison.summary.length, 10) }} most
        similar</AppHeading
      >

      <!-- list of comparison results -->
      <AppFlex>
        <div
          v-for="(match, matchIndex) in comparison.summary.slice(0, 10)"
          :key="matchIndex"
          class="match"
        >
          <!-- ring score -->
          <AppRing
            v-tooltip="'Similarity score'"
            :score="match.score"
            :percent="1 - 1 / (1 + match.score)"
          />
          <!-- for percent, use asymptotic function limited to 1 so we don't need to know max score -->

          <AppFlex class="details" direction="col" align-h="left" gap="small">
            <AppNodeBadge
              :node="{ id: match.source, name: match.source_label }"
            />
            <AppNodeBadge
              :node="{ id: match.target, name: match.target_label }"
            />
          </AppFlex>
        </div>
      </AppFlex>
    </template>

    <!-- phenogrid results -->
    <template v-if="!isEmpty(comparison.phenogrid.cells)">
      <AppHeading>Detailed Comparison</AppHeading>
      <ThePhenogrid :data="comparison.phenogrid" />
      <AppAlert
        >This feature is still under development. Check back soon for
        more!</AppAlert
      >
    </template>
  </AppSection>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { isEmpty, isEqual } from "lodash";
import {
  compareSetToSet,
  // compareSetToTaxon,
  getPhenotypes,
} from "@/api/phenotype-explorer";
import AppAlert from "@/components/AppAlert.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppRing from "@/components/AppRing.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
import ThePhenogrid from "@/components/ThePhenogrid.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { scrollTo } from "@/router";
import { useQuery } from "@/util/composables";
import { parse } from "@/util/object";
import examples from "./phenotype-explorer.json";

/** common tooltip explaining how to use multi-select component */
const multiTooltip = `In this box, you can select phenotypes in 3 ways:<br>
  <ol>
    <li>Search for individual phenotypes</li>
    <li>Search for genes/diseases and get their associated phenotypes</li>
    <li>Paste comma-separated phenotype IDs</li>
  </ol>`;

/** options for mode of second set */
const bModeOptions = [
  { id: "these phenotypes ..." },
  { id: "phenotypes from all genes of ..." },
  { id: "phenotypes from all human diseases" },
];

/**
 * small hard-coded list of taxon options, just for phenotype explorer, so no
 * backend querying needed
 */
const taxons = [
  { id: "9606", label: "human", scientific: "Homo sapiens" },
  { id: "10090", label: "mouse", scientific: "Mus musculus" },
  { id: "7955", label: "zebrafish", scientific: "Danio rerio" },
  { id: "7227", label: "fruitfly", scientific: "Drosophila melanogaster" },
  { id: "6239", label: "worm", scientific: "Caenorhabditis elegans" },
  { id: "8353", label: "frog", scientific: "Xenopus" },
];

// const bTaxonHuman = taxons[0];

/** taxon options for second set */
const bTaxonOptions = taxons.slice(1);

/** example data */
type GeneratedFrom = {
  /** the option (gene/disease/phenotype) that the phenotypes came from */
  option?: Option;
  /** the phenotypes themselves */
  options?: Options;
};

/** first set of phenotypes */
const aPhenotypes = ref<Options>([]);
/** "generated from" helpers after selecting gene or disease */
const aGeneratedFrom = ref<GeneratedFrom>({});
/** selected mode of second set */
const bMode = ref(bModeOptions[0]);
/** selected taxon for second set */
const bTaxon = ref(bTaxonOptions[0]);
/** second set of phenotypes */
const bPhenotypes = ref<Options>([]);
/** "generated from" helpers after selecting gene or disease */
const bGeneratedFrom = ref<GeneratedFrom>({});

/** element reference */
const aBox = ref<{ runSearch: (value: string) => void }>();

/** example phenotype set comparison */
function doExample() {
  aPhenotypes.value = examples.a.options;
  bPhenotypes.value = examples.b.options;
  aGeneratedFrom.value = examples.a;
  bGeneratedFrom.value = examples.b;
  bMode.value = bModeOptions[0];
}

/** comparison analysis */
const {
  query: runAnalysis,
  data: comparison,
  isLoading,
  isError,
} = useQuery(
  async function () {
    scrollToResults();

    // /** run appropriate analysis based on selected mode */
    // if (bMode.value.id.includes("these phenotypes"))
    return await compareSetToSet(
      aPhenotypes.value.map(({ id }) => id),
      bPhenotypes.value.map(({ id }) => id),
    );
    // else
    //   return await compareSetToTaxon(
    //     aPhenotypes.value.map(({ id }) => id),
    //     bMode.value.id.includes("diseases") ? bTaxonHuman.id : bTaxon.value.id,
    //   );
  },

  /** default value */
  { summary: [], phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] } },

  scrollToResults,
);

/** scroll results into view */
async function scrollToResults() {
  scrollTo("#results");
}

/** when multi select component runs spread options function */
function spreadOptions(option: Option, options: Options, set: string) {
  /** notify */
  if (options.length === 0) snackbar("No associated phenotypes found");
  else snackbar(`Selected ${options.length} phenotypes`);

  /** set "generated from" helpers */
  if (set === "a") aGeneratedFrom.value = { option, options };
  else if (set === "b") bGeneratedFrom.value = { option, options };
}

/** clear/reset results */
function clearResults() {
  comparison.value.summary = [];
  comparison.value.phenogrid = { cols: [], rows: [], cells: {}, unmatched: [] };
}

/** get description to show below phenotypes select box */
function description(
  phenotypes: Options,
  generatedFrom: GeneratedFrom,
): string {
  const description = [];

  /** number of phenotypes */
  description.push(`${phenotypes.length} selected`);

  /** to avoid misleading text, only show if lists match exactly */
  if (isEqual(generatedFrom.options, phenotypes))
    description.push(
      `generated from "${
        generatedFrom.option?.label || generatedFrom.option?.id
      }"`,
    );
  return `(${description.join(", ")})`;
}

/** clear results when inputs are changed to avoid de-sync */
watch([aPhenotypes, bMode, bTaxon, bPhenotypes], clearResults, { deep: true });

/** fill in phenotype ids or search from other pages */
onMounted(() => {
  const { phenotypes, search } = window.history.state;
  if (phenotypes) {
    const _phenotypes = parse<Options>(phenotypes, []);
    aPhenotypes.value = _phenotypes;
    aGeneratedFrom.value = {
      option: { id: "text annotator" },
      options: _phenotypes,
    };
  }

  if (search) {
    const _search = parse<string>(search, "");
    aBox.value?.runSearch(_search);
  }
});
</script>

<style lang="scss" scoped>
.weak {
  color: $gray;
  text-align: center;
}

.match {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 40px;
}

.details {
  flex-grow: 1;
  width: 0;
}

.arrow {
  color: $gray;
}

@media (max-width: 600px) {
  .match {
    flex-direction: column;
    margin: 10px 0;
    gap: 20px;
  }

  .details {
    width: 100%;
  }
}
</style>
