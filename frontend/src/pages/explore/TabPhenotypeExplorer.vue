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
    <!-- similarity metric -->
    <AppFlex gap="small">
      <strong>... using metric</strong>
      <AppSelectSingle
        v-model="metric"
        name="Similarity metric"
        :options="metricOptions"
      />
    </AppFlex>
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
    <!-- list of compare results -->
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
          <!-- score -->
          <AppFlex align-h="left" gap="small">
            <tooltip :append-to="appendToBody" :tag="null">
              <AppPercentage
                :score="match.score"
                :percent="ringPercent(match.score)"
                >{{ match.score.toFixed(1) }}</AppPercentage
              >
              <template #content>
                <div class="mini-table">
                  <span>Ancestor</span>
                  <AppNodeBadge
                    :node="{
                      id: match.ancestor_id,
                      name: match.ancestor_label,
                    }"
                    :absolute="true"
                  />
                  <AppLink
                    to="https://incatools.github.io/ontology-access-kit/guide/similarity.html#information-content"
                  >
                    Ancestor IC
                  </AppLink>
                  <span>
                    {{ match.ancestor_information_content?.toFixed(3) }}
                  </span>
                  <AppLink
                    to="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649640/"
                  >
                    Phenodigm
                  </AppLink>
                  <span> {{ match.phenodigm_score?.toFixed(3) }} </span>
                  <AppLink
                    to="https://incatools.github.io/ontology-access-kit/guide/similarity.html#jaccard-similarity"
                  >
                    Jaccard
                  </AppLink>
                  <span>{{ match.jaccard_similarity?.toFixed(3) }}</span>
                </div>
              </template>
            </tooltip>
            <AppIcon
              v-if="match.jaccard_similarity === 1"
              v-tooltip="'Equal by Jaccard similarity'"
              icon="equals"
              tabindex="0"
            />
          </AppFlex>
          <AppNodeBadge
            :node="{ id: match.target, name: match.target_label }"
          />
        </template>
      </div>
    </div>
    <!-- unmatched phenotypes -->
    <template
      v-if="
        (compareTab === 'a-to-b'
          ? compareResults.subjectUnmatched
          : compareResults.objectUnmatched
        ).length
      "
    >
      <AppHeading>Unmatched</AppHeading>
      <AppFlex direction="col">
        <AppNodeBadge
          v-for="(unmatched, index) in compareTab === 'a-to-b'
            ? compareResults.subjectUnmatched
            : compareResults.objectUnmatched"
          :key="index"
          :node="{ id: unmatched.id, name: unmatched.label }"
        />
      </AppFlex>
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
        v-for="(match, index) in searchResults.summary.slice(0, 10)"
        :key="index"
        class="match"
      >
        <!-- score -->
        <AppPercentage
          :percent="ringPercent(match.score)"
          tooltip="Average similarity score"
          >{{ match.score.toFixed(1) }}</AppPercentage
        >
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
import { isEqual } from "lodash";
import {
  compareSetToGroup,
  compareSetToSet,
  getPhenotypes,
  groups,
  metricOptions,
  type Group,
} from "@/api/phenotype-explorer";
import AppAlert from "@/components/AppAlert.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPercentage from "@/components/AppPercentage.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
import AppTabs from "@/components/AppTabs.vue";
import ThePhenogrid from "@/components/ThePhenogrid.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { arrayParam, useParam, type Param } from "@/composables/use-param";
import { useQuery } from "@/composables/use-query";
import { appendToBody } from "@/global/tooltip";
import { scrollTo } from "@/router";
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
  { id: "phenotypes from these genes/diseases ..." },
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

const optionParam: Param<Option> = {
  parse: (value) => ({ id: value }),
  stringify: (value) => String(value.id),
};
const optionsParam = arrayParam<Option>({
  parse: (value) => (value ? { id: value } : undefined),
  stringify: (value) => String(value.id),
});

/** first set of phenotypes */
const aPhenotypes = useParam<Options>("a-set", optionsParam, []);
/** "generated from" helpers after selecting gene or disease */
const aGeneratedFrom = ref<GeneratedFrom>({});
/** selected mode of second set */
const bMode = useParam("b-mode", optionParam, bModeOptions[0]);
/** selected group for second set */
const bGroup = useParam("b-group", optionParam, bGroupOptions[0]);
/** second set of phenotypes */
const bPhenotypes = useParam<Options>("b-set", optionsParam, []);
/** "generated from" helpers after selecting gene or disease */
const bGeneratedFrom = ref<GeneratedFrom>({});
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
      metric.value.id,
    );
  },

  /** default value */
  {
    subjectMatches: [],
    objectMatches: [],
    subjectUnmatched: [],
    objectUnmatched: [],
  },

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
    subjectMatches: [],
    objectMatches: [],
    subjectUnmatched: [],
    objectUnmatched: [],
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

/** clear results when inputs are changed to avoid de-sync */
watch([aPhenotypes, bMode, bGroup, bPhenotypes, metric], clearResults, {
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
