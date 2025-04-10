<template>
  <AppBreadcrumb />
  <PageTitle title="Phenotype Similarity Compare" id="phenotype-compare" />

  <AppSection design="bare">
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

    <strong>... to these phenotypes</strong>
    <AppSelectTags
      v-model="bPhenotypes"
      name="Second set of phenotypes"
      :options="getPhenotypes"
      placeholder="Search for phenotypes, genes, or diseases"
      :tooltip="multiTooltip"
      :description="description(bPhenotypes, bGeneratedFrom)"
      @spread-options="(option, options) => spreadOptions(option, options, 'b')"
    />

    <!-- Metric Selection -->
    <AppFlex gap="small">
      <strong>... using metric</strong>
      <AppSelectSingle
        v-model="metric"
        name="Similarity metric"
        :options="metricOptions"
      />
    </AppFlex>

    <!-- Analyze Button -->
    <AppButton
      text="Analyze"
      icon="bars-progress"
      :disabled="isPending || isBlank"
      @click="runCompare()"
    />
  </AppSection>

  <!-- Analysis Status -->
  <AppSection v-if="isPending">
    <AppStatus v-if="compareIsLoading" code="loading"
      >Running analysis</AppStatus
    >
    <AppStatus v-if="compareIsError" code="error"
      >Error running analysis</AppStatus
    >
  </AppSection>

  <!-- Compare Results -->
  <AppSection
    v-else-if="
      compareResults.subjectMatches.length ||
      compareResults.objectMatches.length ||
      compareResults.subjectUnmatched.length ||
      compareResults.objectUnmatched.length
    "
  >
    <AppHeading>Similarity Comparison</AppHeading>

    <AppTabs
      v-model="compareTab"
      name="Comparison direction"
      :tabs="compareTabs"
      :url="false"
    />

    <div class="triptych-scroll">
      <div class="triptych">
        <div>
          <strong>{{ headings[0].name }}</strong>
          <div class="weak">{{ headings[0].description }}</div>
        </div>
        <strong>Match</strong>
        <div>
          <strong>{{ headings[1].name }}</strong>
          <div class="weak">{{ headings[1].description }}</div>
        </div>

        <template
          v-for="(match, index) in compareTab === 'a-to-b'
            ? compareResults.subjectMatches
            : compareResults.objectMatches"
          :key="index"
        >
          <AppNodeBadgeV2
            :node="{ id: match.source, name: match.source_label }"
          />

          <!-- Score -->
          <AppFlex align-h="left" gap="small">
            <AppPercentage
              :score="match.score"
              :percent="ringPercent(match.score)"
              >{{ match.score.toFixed(1) }}</AppPercentage
            >
          </AppFlex>

          <AppNodeBadgeV2
            :node="{ id: match.target, name: match.target_label }"
          />
        </template>
      </div>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import {
  compareSetToSet,
  getPhenotypes,
  metricOptions,
} from "@/api/phenotype-explorer";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppButton from "@/components/AppButton.vue";
import AppNodeBadgeV2 from "@/components/AppNodeBadgeV2.vue";
import AppPercentage from "@/components/AppPercentage.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
import AppTabs from "@/components/AppTabs.vue";
import PageTitle from "@/components/PageTitle.vue";
import { usePhenotypeSets } from "@/composables/use-phenotype-sets";
import { useQuery } from "@/composables/use-query";
import examples from "@/data/phenotype-explorer.json";

const {
  aPhenotypes,
  bPhenotypes,
  aGeneratedFrom,
  bGeneratedFrom,
  description,
  spreadOptions,
} = usePhenotypeSets();

/** Tooltip for multi-select component */
const multiTooltip = `In this box, you can select phenotypes in 3 ways:<br>
  <ol>
    <li>Search for individual phenotypes</li>
    <li>Search for genes/diseases and get their associated phenotypes</li>
    <li>Paste comma-separated phenotype IDs</li>
  </ol>`;

/** Metric for comparison */
const metric = ref<Option>(metricOptions[0]);

/** compare tab options */
const compareTabs = [
  { id: "a-to-b", text: "A → B" },
  { id: "b-to-a", text: "B → A" },
] as const;

/** currently selected compare tab */
const compareTab = ref<(typeof compareTabs)[number]["id"]>("a-to-b");

/** headings for compare table */
const headings = computed(() => {
  const headings = [
    {
      name: "Set A",
      description: description(aPhenotypes.value, aGeneratedFrom.value),
    },
    {
      name: "Set B",
      description: description(bPhenotypes.value, bGeneratedFrom.value),
    },
  ];

  if (compareTab.value === "b-to-a") headings.reverse();

  return headings;
});

/** Example phenotype set comparison */
function doSimpleExample() {
  aPhenotypes.value = examples.a.options;
  bPhenotypes.value = examples.b.options;
  aGeneratedFrom.value = examples.a;
  bGeneratedFrom.value = examples.b;
}

function doBiggerExample() {
  aPhenotypes.value = examples.c.options;
  bPhenotypes.value = examples.d.options;
  aGeneratedFrom.value = examples.c;
  bGeneratedFrom.value = examples.d;
}

/** Comparison results */
const {
  query: runCompare,
  data: compareResults,
  isLoading: compareIsLoading,
  isError: compareIsError,
} = useQuery(
  async () => {
    return await compareSetToSet(
      aPhenotypes.value.map(({ id }) => id),
      bPhenotypes.value.map(({ id }) => id),
      metric.value.id,
    );
  },
  {
    subjectMatches: [],
    objectMatches: [],
    subjectUnmatched: [],
    objectUnmatched: [],
  },
);
console.log("compareResults", compareResults);
/** Whether analysis is pending */
const isPending = computed(
  () => compareIsLoading.value || compareIsError.value,
);
/** Whether inputs are blank */
const isBlank = computed(
  () => !aPhenotypes.value.length || !bPhenotypes.value.length,
);

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
</script>

<style lang="scss" scoped>
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
</style>
