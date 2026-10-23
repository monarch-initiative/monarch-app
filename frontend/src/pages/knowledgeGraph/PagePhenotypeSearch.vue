<template>
  <AppSection width="big">
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
    <AppFlex gap="small" class="select-single">
      <strong>Find</strong>
      <AppSelectSingle
        v-model="bGroup"
        name="Second set taxon"
        :options="bGroupOptions"
      />
    </AppFlex>
    <AppFlex gap="small" direction="col">
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
      />
    </AppFlex>
    <AppFlex gap="small" class="select-single">
      <strong>... using metric</strong>
      <AppSelectSingle
        v-model="metric"
        name="Similarity metric"
        :options="metricOptions"
      />
    </AppFlex>
    <AppAccordion text="Advanced ranking settings" icon="wrench">
      <AppFlex gap="small" direction="col" align-h="left">
        <AppFlex gap="small" class="select-single">
          <strong>Score by</strong>
          <AppSelectSingle
            v-model="directionality"
            name="Score direction"
            :options="directionalityOptions"
          />
        </AppFlex>
        <AppFlex gap="small" class="select-single">
          <strong>Candidates</strong>
          <AppSelectSingle
            v-model="searchMode"
            name="Search mode"
            :options="searchModeOptions"
          />
        </AppFlex>
        <AppFlex gap="small" class="select-single">
          <strong>Information content from</strong>
          <AppSelectSingle
            v-model="informationContent"
            name="Information content source"
            :options="informationContentOptions"
          />
        </AppFlex>
        <AppFlex gap="small" class="select-single">
          <strong>Break ties</strong>
          <AppSelectSingle
            v-model="tieBreak"
            name="Tie-break"
            :options="tieBreakOptions"
          />
        </AppFlex>
        <p class="settings-help">
          The defaults reproduce the current ranking. "How much of the query
          each result covers" doesn't penalize results with many phenotypes, and
          scoring every entity keeps them from being dropped before scoring.
          Annotation-based information content makes rarely annotated phenotypes
          count for more. These settings are experimental.
        </p>
      </AppFlex>
    </AppAccordion>
    <AppButton
      text="Analyze"
      icon="bars-progress"
      :disabled="isPending || isBlank"
      @click="runSearch()"
    />
  </AppSection>
  <!-- analysis status -->
  <AppSection v-if="isPending">
    <AppStatus v-if="searchIsLoading" code="loading"
      >Running analysis</AppStatus
    >
    <AppStatus v-if="searchIsError" code="error"
      >Error running analysis</AppStatus
    >
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
          <span
            v-if="match.objectToSubjectScore !== undefined"
            class="direction-scores"
          >
            <span
              v-tooltip="
                'Average best-match score of the query phenotypes against this result'
              "
              >Query covered: {{ match.objectToSubjectScore?.toFixed(1) }}</span
            >
            ·
            <span
              v-tooltip="
                'Average best-match score of the phenotypes of this result against the query'
              "
              >Result covered:
              {{ match.subjectToObjectScore?.toFixed(1) }}</span
            >
          </span>
        </AppFlex>
      </div>
    </AppFlex>
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
import {
  compareSetToGroup,
  directionalityOptions,
  getPhenotypes,
  groups,
  informationContentOptions,
  metricOptions,
  searchModeOptions,
  tieBreakOptions,
  type Group,
} from "@/api/phenotype-explorer";
import AppAccordion from "@/components/AppAccordion.vue";
import AppAlert from "@/components/AppAlert.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPercentage from "@/components/AppPercentage.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
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

/**
 * url param for one of a fixed list of options. unknown values fall back to the
 * first (the default).
 */
const choiceParam = (options: Options): Param<Option> => ({
  parse: (value) => options.find((option) => option.id === value) || options[0],
  stringify: (value) => String(value.id),
});

/** ranking settings, synced to the url so a shared link reproduces the ranking */
const directionality = useParam(
  "direction",
  choiceParam(directionalityOptions),
  directionalityOptions[0],
);
const searchMode = useParam(
  "search-mode",
  choiceParam(searchModeOptions),
  searchModeOptions[0],
);
const informationContent = useParam(
  "information-content",
  choiceParam(informationContentOptions),
  informationContentOptions[0],
);
const tieBreak = useParam(
  "tie-break",
  choiceParam(tieBreakOptions),
  tieBreakOptions[0],
);

/** element reference */
const aBox = ref<InstanceType<typeof AppSelectTags>>();

/**
 * get % for showing ring based on the selected metric. annotation-based
 * information content tops out lower (log2 of the corpus size, about 13 bits
 * for diseases) than ontology-based (about 19 bits), so its range is smaller.
 */
function ringPercent(score = 0) {
  const id = metric.value.id;
  const annotation = informationContent.value.id === "annotation";
  let min = 0;
  if (id === "ancestor_information_content") min = annotation ? 0 : 4;
  else if (id === "jaccard_similarity") min = 0;
  else if (id === "phenodigm_score") min = annotation ? 0 : 0.1;
  let max = 1;
  if (id === "ancestor_information_content") max = annotation ? 14 : 19;
  else if (id === "jaccard_similarity") max = 1;
  else if (id === "phenodigm_score") max = annotation ? 4 : 5;
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
      {
        directionality: String(directionality.value.id),
        search_mode: String(searchMode.value.id),
        information_content: String(informationContent.value.id),
        tie_break: String(tieBreak.value.id),
      },
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

watch(
  [
    aPhenotypes,
    bGroup,
    metric,
    directionality,
    searchMode,
    informationContent,
    tieBreak,
  ],
  clearResults,
  {
    deep: true,
  },
);

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
.direction-scores {
  color: $gray;
  font-size: 0.9rem;
}
.settings-help {
  max-width: 40em;
  color: $gray;
  font-size: 0.9rem;
}
p {
  text-align: left;
}
</style>
