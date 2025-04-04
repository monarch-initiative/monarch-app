<template>
  <AppSection>
    <!-- Example Buttons -->
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
          <AppNodeBadge
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

          <AppNodeBadge
            :node="{ id: match.target, name: match.target_label }"
          />
        </template>
      </div>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { isEqual } from "lodash";
import {
  compareSetToSet,
  getPhenotypes,
  metricOptions,
} from "@/api/phenotype-explorer";
import AppButton from "@/components/AppButton.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPercentage from "@/components/AppPercentage.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
import AppTabs from "@/components/AppTabs.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { useQuery } from "@/composables/use-query";
import examples from "@/data/phenotype-explorer.json";

/** Tooltip for multi-select component */
const multiTooltip = `In this box, you can select phenotypes in 3 ways:<br>
  <ol>
    <li>Search for individual phenotypes</li>
    <li>Search for genes/diseases and get their associated phenotypes</li>
    <li>Paste comma-separated phenotype IDs</li>
  </ol>`;

/** example data */
type GeneratedFrom = {
  /** the option (gene/disease/phenotype) that the phenotypes came from */
  option?: Option;
  /** the phenotypes themselves */
  options?: Options;
};

/** First set of phenotypes */
const aPhenotypes = ref<Options>([]);
/** Second set of phenotypes */
const bPhenotypes = ref<Options>([]);
/** Metric for comparison */
const metric = ref<Option>(metricOptions[0]);
/** "generated from" helpers after selecting gene or disease */
const aGeneratedFrom = ref<GeneratedFrom>({});
const bGeneratedFrom = ref({});

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

/** get description to show below phenotypes select box */
function description(
  phenotypes: Options,
  generatedFrom: GeneratedFrom,
): string {
  const description = [];

  /** number of phenotypes */
  description.push(`${phenotypes.length} phenotypes`);

  /** to avoid misleading text, only show if lists match exactly */
  if (isEqual(generatedFrom.options, phenotypes))
    description.push(
      `generated from "${
        generatedFrom.option?.label || generatedFrom.option?.id
      }"`,
    );
  return `(${description.join(", ")})`;
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
