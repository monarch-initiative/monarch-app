<!--
  phenotype explorer tab on explore page

  compare sets of phenotypes and genes/diseases
-->

<template>
  <AppSection>
    <!-- example -->
    <AppFlex gap="small">
      <AppButton
        text="Try a simple example"
        design="small"
        @click="doSimpleExample()"
      />
      |
      <AppButton
        text="Try a bigger example"
        design="small"
        @click="doBiggerExample()"
      />
    </AppFlex>
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
        v-if="!isCompare"
        v-model="bGroup"
        name="Second set taxon"
        :options="bGroupOptions"
      />
    </AppFlex>

    <AppSelectTags
      v-if="isCompare"
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
      text="Analyze"
      icon="bars-progress"
      :disabled="isPending || isBlank"
      @click="isCompare ? runCompare() : runSearch()"
    />
  </AppSection>

  <!-- analysis status -->
  <AppSection v-if="isPending">
    <AppStatus v-if="compareIsLoading || searchIsLoading" code="loading"
      >Running analysis</AppStatus
    >
    <AppStatus v-if="compareIsError || searchIsError" code="error"
      >Error running analysis</AppStatus
    >
  </AppSection>

  <!-- compare results -->
  <AppSection v-else-if="compareResults.summary.length">
    <AppHeading>Similarity Comparison</AppHeading>

    <!-- heading -->
    <AppHeading
      >Top {{ Math.min(compareResults.summary.length, 10) }} most
      similar</AppHeading
    >

    <!-- list of compare results -->
    <AppFlex>
      <div
        v-for="(match, matchIndex) in compareResults.summary.slice(0, 10)"
        :key="matchIndex"
        class="match"
      >
        <!-- ring score -->
        <AppRing
          v-tooltip="'Similarity score'"
          :score="match.score"
          :percent="ringPercent(match.score)"
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

    <!-- phenogrid results -->
    <template v-if="!isEmpty(compareResults.phenogrid.cells)">
      <AppHeading>Detailed Comparison</AppHeading>
      <ThePhenogrid :data="compareResults.phenogrid" />
      <AppAlert
        >This feature is still under development. Check back soon for
        more!</AppAlert
      >
    </template>
  </AppSection>

  <!-- search results -->
  <AppSection v-else-if="searchResults.summary.length">
    <AppHeading>Similarity Comparison</AppHeading>

    <!-- heading -->
    <AppHeading
      >Top {{ Math.min(searchResults.summary.length, 10) }} most
      similar</AppHeading
    >

    <!-- list of search results -->
    <AppFlex>
      <div
        v-for="(match, matchIndex) in searchResults.summary.slice(0, 10)"
        :key="matchIndex"
        class="match"
      >
        <!-- ring score -->
        <AppRing
          v-tooltip="'Similarity score'"
          :score="match.score"
          :percent="ringPercent(match.score)"
        />
        <!-- for percent, use asymptotic function limited to 1 so we don't need to know max score -->

        <AppFlex class="details" direction="col" align-h="left" gap="small">
          <AppNodeBadge :node="match.subject" />
        </AppFlex>
      </div>
    </AppFlex>

    <!-- phenogrid results -->
    <AppHeading>Detailed Comparison</AppHeading>
    <ThePhenogrid :data="searchResults.phenogrid" />
    <AppAlert
      >This feature is still under development. Check back soon for
      more!</AppAlert
    >
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { isEmpty, isEqual } from "lodash";
import {
  compareSetToGroup,
  compareSetToSet,
  getPhenotypes,
  groups,
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
  { id: "phenotypes from all ..." },
];

/** search group options */
const bGroupOptions = groups.map((group) => ({ id: group, label: group }));

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
/** selected group for second set */
const bGroup = ref(bGroupOptions[0]);
/** second set of phenotypes */
const bPhenotypes = ref<Options>([]);
/** "generated from" helpers after selecting gene or disease */
const bGeneratedFrom = ref<GeneratedFrom>({});

/** element reference */
const aBox = ref<{ runSearch: (value: string) => void }>();

/** get % for showing ring. domain 1 to ~20 (asymptotic), range 0 to 1 */
function ringPercent(score = 0) {
  return (score - 1) / (5 + score - 1);
}

/** example phenotype set comparison */
function doSimpleExample() {
  aPhenotypes.value = examples.a.options;
  bPhenotypes.value = examples.b.options;
  aGeneratedFrom.value = examples.a;
  bGeneratedFrom.value = examples.b;
  bMode.value = bModeOptions[0];
}

function doBiggerExample() {
  aPhenotypes.value = examples.c.options;
  bPhenotypes.value = examples.d.options;
  aGeneratedFrom.value = examples.c;
  bGeneratedFrom.value = examples.d;
  bMode.value = bModeOptions[0];
}

/** comparison analysis */
const {
  query: runCompare,
  data: compareResults,
  isLoading: compareIsLoading,
  isError: compareIsError,
} = useQuery(
  async function () {
    scrollToResults();

    return await compareSetToSet(
      aPhenotypes.value.map(({ id }) => id),
      bPhenotypes.value.map(({ id }) => id),
    );
  },

  /** default value */
  { summary: [], phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] } },

  scrollToResults,
);

/** search analysis */
const {
  query: runSearch,
  data: searchResults,
  isLoading: searchIsLoading,
  isError: searchIsError,
} = useQuery(
  async function () {
    scrollToResults();

    return await compareSetToGroup(
      aPhenotypes.value.map(({ id }) => id),
      bGroup.value.id,
    );
  },

  /** default value */
  { summary: [], phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] } },

  scrollToResults,
);

/** scroll results into view */
async function scrollToResults() {
  scrollTo("#results");
}

/** current mode */
const isCompare = computed(() => bMode.value.id.includes("these phenotypes"));

/** is in loading/error state */
const isPending = computed(() =>
  isCompare.value
    ? compareIsLoading.value || compareIsError.value
    : searchIsLoading.value || searchIsError.value,
);

/** whether user hasn't inputted anything to analyze */
const isBlank = computed(
  () =>
    !aPhenotypes.value.length || (isCompare.value && !bPhenotypes.value.length),
);

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
  compareResults.value = {
    summary: [],
    phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] },
  };
  searchResults.value = {
    summary: [],
    phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] },
  };
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
watch([aPhenotypes, bMode, bGroup, bPhenotypes], clearResults, { deep: true });

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
