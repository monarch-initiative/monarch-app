<template>
   <AppBreadcrumb /> <PageTitle
    id="phenotype-search"
    title="Phenotype Similarity Search"
  /> <AppSection design="bare"
    >
    <p class="description">
       Phenotype similarity search tool finds genes or diseases from a selected
      species or group that show phenotypic similarity to a set of input
      phenotypes. Similarity is computed using semantic metrics such as Jaccard,
      Information Content, or Phenodigm.
    </p>
     <AppFlex gap="small"
      > <AppButton
        text="Try a simple example"
        design="small"
        @click="doSimpleExample()"
      /> | <AppButton
        text="Try a bigger example"
        design="small"
        @click="doBiggerExample()"
      /> </AppFlex
    > <AppFlex gap="small" class="select-single"
      > <strong>Find</strong> <AppSelectSingle
        v-model="bGroup"
        name="Second set taxon"
        :options="bGroupOptions"
      /> </AppFlex
    > <AppFlex gap="small" direction="col"
      >
      <div class="label">similar to phenotypes..</div>
       <AppSelectTags
        ref="aBox"
        v-model="aPhenotypes"
        name="Phenotypes"
        :options="getPhenotypes"
        placeholder="Search for phenotypes, genes, or diseases"
        :tooltip="multiTooltip"
        :description="description(aPhenotypes, aGeneratedFrom)"
        @spread-options="
          (option, options) => spreadOptions(option, options, 'a')
        "
      /> </AppFlex
    > <AppFlex gap="small" class="select-single"
      > <strong>... using metric</strong> <AppSelectSingle
        v-model="metric"
        name="Similarity metric"
        :options="metricOptions"
      /> </AppFlex
    > <AppButton
      text="Analyze"
      icon="bars-progress"
      :disabled="isPending || isBlank"
      @click="runSearch()"
    /> </AppSection
  > <!-- analysis status --> <AppSection v-if="isPending"
    > <AppStatus v-if="searchIsLoading" code="loading"
      >Running analysis</AppStatus
    > <AppStatus v-if="searchIsError" code="error"
      >Error running analysis</AppStatus
    > </AppSection
  > <!-- search results --> <AppSection v-else-if="searchResults.summary.length"
    > <AppHeading>Similarity Comparison</AppHeading> <!-- heading -->
    <AppHeading
      >Top {{ Math.min(searchResults.summary.length, 10) }} most
      similar</AppHeading
    > <!-- list of search results --> <AppFlex
      >
      <div
        v-for="(match, index) in searchResults.summary.slice(0, 10)"
        :key="index"
        class="match"
      >
         <!-- score --> <AppPercentage
          :percent="ringPercent(match.score)"
          tooltip="Average similarity score"
          >{{ match.score.toFixed(1) }}</AppPercentage
        > <AppFlex class="details" direction="col" align-h="left" gap="small"
          > <AppNodeBadgeV2 :node="match.subject" /> </AppFlex
        >
      </div>
       </AppFlex
    > <AppHeading>Detailed Comparison</AppHeading> <ThePhenogrid
      :data="searchResults.phenogrid"
    /> <AppAlert
      >This feature is still under development. Check back soon for
      more!</AppAlert
    > </AppSection
  >
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import {
  compareSetToGroup,
  getPhenotypes,
  groups,
  metricOptions,
  type Group,
} from "@/api/phenotype-explorer";
import AppAlert from "@/components/AppAlert.vue";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppNodeBadgeV2 from "@/components/AppNodeBadgeV2.vue";
import AppPercentage from "@/components/AppPercentage.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import ThePhenogrid from "@/components/ThePhenogrid.vue";
import { useParam, type Param } from "@/composables/use-param";
import { usePhenotypeSets } from "@/composables/use-phenotype-sets";
import { useQuery } from "@/composables/use-query";
import examples from "@/data/phenotype-explorer.json";
import { scrollTo } from "@/router";
import { parse } from "@/util/object";

const { aPhenotypes, aGeneratedFrom, description, spreadOptions } =
  usePhenotypeSets();

/** common tooltip explaining how to use multi-select component */
const multiTooltip = `In this box, you can select phenotypes in 3 ways:<br>
  <ol>
    <li>Search for individual phenotypes</li>
    <li>Search for genes/diseases and get their associated phenotypes</li>
    <li>Paste comma-separated phenotype IDs</li>
  </ol>`;

/** search group options */
const bGroupOptions = groups.map((group) => ({ id: group, label: group }));

const optionParam: Param<Option> = {
  parse: (value) => ({ id: value }),
  stringify: (value) => String(value.id),
};

/** selected group for second set */
const bGroup = useParam("b-group", optionParam, bGroupOptions[0]);

/** selected metric */
const metric = ref<Option>(metricOptions[0]);

/** element reference */
const aBox = ref<InstanceType<typeof AppSelectTags>>();

/** get % for showing ring based on the selected metric */
function ringPercent(score = 0) {
  const id = metric.value.id;
  let min = 0;
  if (id === "ancestor_information_content") min = 4;
  else if (id === "jaccard_similarity") min = 0;
  else if (id === "phenodigm_score") min = 0.1;
  let max = 1;
  if (id === "ancestor_information_content") max = 19;
  else if (id === "jaccard_similarity") max = 1;
  else if (id === "phenodigm_score") max = 5;
  return (score - min) / (max - min);
}

/** example phenotype set comparison */
function doSimpleExample() {
  aPhenotypes.value = examples.a.options;
  aGeneratedFrom.value = examples.a;
}

function doBiggerExample() {
  aPhenotypes.value = examples.c.options;
  aGeneratedFrom.value = examples.c;
}

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
      bGroup.value.id as Group,
      metric.value.id,
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

/** is in loading/error state */
const isPending = computed(() => searchIsLoading.value || searchIsError.value);

/** whether user hasn't inputted anything to analyze */
const isBlank = computed(() => !aPhenotypes.value.length);

/** clear/reset results */
function clearResults() {
  searchResults.value = {
    summary: [],
    phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] },
  };
}

watch([aPhenotypes, bGroup, metric], clearResults, {
  deep: true,
});

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
$wrap: 1000px;
.triptych-scroll {
  width: 100%;
  overflow-x: auto;
}

.triptych {
  display: grid;
  grid-template-columns: 1fr max-content 1fr;
  min-width: 400px;
  gap: 20px 40px;
}

.weak {
  color: $gray;
}

.triptych > :nth-child(3n + 1) {
  justify-self: flex-start;
  text-align: left;
}

.triptych > :nth-child(3n) {
  justify-self: flex-end;
  text-align: right;
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
.label {
  width: auto;
  min-width: fit-content;
  font-weight: 600;
}
.select-single {
  min-width: 19em;
  max-width: 35em;
}
.description {
  text-align: left;
}
p {
  text-align: left;
}
</style>

