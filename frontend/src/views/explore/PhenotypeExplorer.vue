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
      v-model="aPhenotypes"
      name="First set of phenotypes"
      :options="getPhenotypes"
      placeholder="Select phenotypes"
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
      placeholder="Select phenotypes"
      :tooltip="multiTooltip"
      :description="description(bPhenotypes, bGeneratedFrom)"
      @spread-options="(option, options) => spreadOptions(option, options, 'b')"
    />

    <!-- run analysis -->
    <AppButton text="Analyze" icon="bars-progress" @click="runAnalysis" />
  </AppSection>

  <AppSection>
    <!-- analysis status -->
    <AppStatus v-if="isLoading" code="loading">Running analysis</AppStatus>
    <AppStatus v-if="isError" code="error">Error running analysis</AppStatus>

    <!-- analysis top results -->
    <AppFlex v-else-if="comparison.matches.length">
      <!-- heading -->
      <strong
        >Top {{ Math.min(comparison.matches.length, 10) }} match(es)</strong
      >

      <!-- list of comparison results -->
      <div
        v-for="(match, matchIndex) in comparison.matches.slice(0, 10)"
        :key="matchIndex"
        class="match"
      >
        <!-- ring score -->
        <AppRing
          v-tooltip="'Similarity score'"
          :score="match.score"
          :min="comparison.minScore"
          :max="comparison.maxScore"
        />

        <AppFlex direction="col" h-align="stretch" gap="small" class="details">
          <!-- primary match info -->
          <div class="primary truncate">
            <AppIcon
              v-tooltip="startCase(match.category)"
              :icon="`category-${match.category}`"
            />

            <!-- if name of match is + separated list of phenotype ids, link to each one separately -->
            <template v-if="match.name.includes(' + ')">
              <template
                v-for="(id, idIndex) of match.name.split(' + ')"
                :key="idIndex"
              >
                <AppLink :to="`/${kebabCase(match.category)}/${id}`">
                  {{ id }}
                </AppLink>
                <span v-if="idIndex !== match.name.split(' + ').length - 1">
                  +
                </span>
              </template>
            </template>

            <!-- otherwise, just show details as normal -->
            <template v-else>
              <AppLink :to="`/${kebabCase(match.category)}/${match.id}`">
                {{ match.name }}
              </AppLink>
            </template>
          </div>

          <!-- secondary match info -->
          <div class="secondary truncate">
            <span>{{ match.id }}</span>
            <span v-if="match.taxon">&nbsp; | &nbsp;{{ match.taxon }}</span>
          </div>
        </AppFlex>
      </div>
    </AppFlex>

    <!-- phenogrid results -->
    <template v-if="comparison.matches.length">
      <strong>Phenotype Similarity Comparison</strong>
      <div id="phenogrid"></div>
    </template>
  </AppSection>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { isEqual, kebabCase, startCase } from "lodash";
import { mountPhenogrid } from "@/api/phenogrid";
import {
  compareSetToSet,
  compareSetToTaxon,
  getPhenotypes,
} from "@/api/phenotype-explorer";
import AppRing from "@/components/AppRing.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { useQuery } from "@/util/composables";
import { parse } from "@/util/object";
import examples from "./phenotype-explorer.json";

/** Common tooltip explaining how to use multi-select component */
const multiTooltip = `In this box, you can select phenotypes in 3 ways:<br>
  <ol>
    <li>Search for individual phenotypes</li>
    <li>Search for genes/diseases and get their associated phenotypes</li>
    <li>Paste comma-separated phenotype IDs</li>
  </ol>`;

/** Options for mode of second set */
const bModeOptions = [
  { id: "these phenotypes ..." },
  { id: "phenotypes from all genes of ..." },
  { id: "phenotypes from all human diseases" },
];

/**
 * Small hard-coded list of taxon options, just for phenotype explorer, so no
 * backend querying needed
 */
const taxons = [
  { id: "9606", name: "human", scientific: "Homo sapiens" },
  { id: "10090", name: "mouse", scientific: "Mus musculus" },
  { id: "7955", name: "zebrafish", scientific: "Danio rerio" },
  { id: "7227", name: "fruitfly", scientific: "Drosophila melanogaster" },
  { id: "6239", name: "worm", scientific: "Caenorhabditis elegans" },
  { id: "8353", name: "frog", scientific: "Xenopus" },
];

const bTaxonHuman = taxons[0];

/** Taxon options for second set */
const bTaxonOptions = taxons.slice(1);

/** Example data */
type GeneratedFrom = {
  /** The option (gene/disease/phenotype) that the phenotypes came from */
  option?: Option;
  /** The phenotypes themselves */
  options?: Options;
}

/** First set of phenotypes */
const aPhenotypes = ref([] as Options);
/** "generated from" helpers after selecting gene or disease */
const aGeneratedFrom = ref({} as GeneratedFrom);
/** Selected mode of second set */
const bMode = ref(bModeOptions[0]);
/** Selected taxon for second set */
const bTaxon = ref(bTaxonOptions[0]);
/** Second set of phenotypes */
const bPhenotypes = ref([] as Options);
/** "generated from" helpers after selecting gene or disease */
const bGeneratedFrom = ref({} as GeneratedFrom);

/** Example phenotype set comparison */
function doExample() {
  aPhenotypes.value = examples.a.options;
  bPhenotypes.value = examples.b.options;
  aGeneratedFrom.value = examples.a;
  bGeneratedFrom.value = examples.b;
}

/** Comparison analysis */
const {
  query: runAnalysis,
  data: comparison,
  isLoading,
  isError,
} = useQuery(
  async function () {
    /** Run appropriate analysis based on selected mode */
    if (bMode.value.id.includes("these phenotypes"))
      return await compareSetToSet(
        aPhenotypes.value.map(({ id }) => id),
        bPhenotypes.value.map(({ id }) => id)
      );
    else
      return await compareSetToTaxon(
        aPhenotypes.value.map(({ id }) => id),
        bMode.value.id.includes("diseases") ? bTaxonHuman.id : bTaxon.value.id
      );
  },

  /** Default value */
  { matches: [] }
);

/** When multi select component runs spread options function */
function spreadOptions(option: Option, options: Options, set: string) {
  /** Notify */
  if (options.length === 0) snackbar("No associated phenotypes found");
  else snackbar(`Selected ${options.length} phenotypes`);

  /** Set "generated from" helpers */
  if (set === "a") aGeneratedFrom.value = { option, options };
  else if (set === "b") bGeneratedFrom.value = { option, options };
}

/** Show phenogrid results */
function runPhenogrid() {
  /** Which biolink /sim endpoint to use */
  const mode = bMode.value.id.includes("these phenotypes")
    ? "compare"
    : "search";

  /** Use first group of phenotypes for y axis */
  const yAxis = aPhenotypes.value;

  /** Use second taxon id or group of phenotypes as x axis */
  let xAxis = [];
  if (mode === "compare") xAxis = bPhenotypes.value;
  else {
    const taxon = bMode.value.id.includes("diseases")
      ? bTaxonHuman
      : bTaxon.value;
    xAxis = [{ id: taxon.id, name: taxon.scientific }];
  }
  /** Call phenogrid */
  mountPhenogrid("#phenogrid", xAxis, yAxis, mode);
}

/** Run phenogrid, attach to div container */
watch(
  () => comparison.value,
  () => {
    if (comparison.value.matches.length) runPhenogrid();
  }
);

/** Clear/reset results */
function clearResults() {
  comparison.value = { matches: [] };
}

/** Get description to show below phenotypes select box */
function description(
  phenotypes: Options,
  generatedFrom: GeneratedFrom
): string {
  const description = [];

  /** Number of phenotypes */
  description.push(`${phenotypes.length} selected`);

  /** To avoid misleading text, only show if lists match exactly */
  if (isEqual(generatedFrom.options, phenotypes))
    description.push(
      `generated from "${
        generatedFrom.option?.name || generatedFrom.option?.id
      }"`
    );
  return `(${description.join(", ")})`;
}

/** Clear results when inputs are changed to avoid de-sync */
watch([aPhenotypes, bMode, bTaxon, bPhenotypes], clearResults, { deep: true });

/** Fill in phenotype ids from text annotator */
onMounted(() => {
  if (window.history.state.phenotypes) {
    const phenotypes = parse(window.history.state.phenotypes, []) as Options;
    aPhenotypes.value = phenotypes;
    aGeneratedFrom.value = {
      option: { id: "text annotator" },
      options: phenotypes,
    };
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
  text-align: left;

  svg {
    margin-right: 10px;
    vertical-align: middle;
  }
}
.primary {
  text-align: left;
}

.secondary {
  color: $gray;
  text-align: left;
}

@media (max-width: 600px) {
  .match {
    flex-direction: column;
    gap: 20px;
    margin: 10px 0;
  }

  .details {
    width: 100%;
  }
}

#phenogrid {
  width: 100%;
}
</style>
