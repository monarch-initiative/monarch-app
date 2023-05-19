<!--
  about sources page

  detailed information on all datasets and ontologies involved in the monarch
  knowledge graph.
-->

<template>
  <AppSection>
    <AppHeading>Sources</AppHeading>

    <!-- filters -->
    <AppFlex>
      <AppCheckbox
        v-model="showDatasets"
        :text="`Datasets (${datasetCount})`"
        icon="database"
      />
      <AppCheckbox
        v-model="showOntologies"
        :text="`Ontologies (${ontologyCount})`"
        icon="puzzle-piece"
      />
    </AppFlex>

    <!-- status -->
    <AppStatus v-if="isLoading" code="loading">Loading sources</AppStatus>
    <AppStatus v-if="isError" code="error">Error loading sources</AppStatus>

    <!-- list of all sources -->
    <AppFlex direction="col">
      <AppAccordion
        v-for="(source, sourceIndex) in filteredSources"
        :key="sourceIndex"
        :text="source.name || source.id || ''"
        :icon="source.type === 'dataset' ? 'database' : 'puzzle-piece'"
      >
        <!-- row of details and links -->
        <AppFlex>
          <AppButton
            v-if="source.link"
            v-tooltip="'Homepage or repository for this source'"
            design="small"
            icon="home"
            text="Home"
            :to="source.link"
          />
          <AppButton
            v-if="source.license"
            v-tooltip="'Link to licensing information for this source'"
            design="small"
            icon="balance-scale"
            text="License"
            :to="source.license"
          />
          <AppButton
            v-if="source.distribution"
            v-tooltip="'Download Resource Description Framework file'"
            design="small"
            icon="download"
            text="RDF"
            :to="source.distribution"
          />
          <AppButton
            v-if="source.date"
            v-tooltip="'Date when this source was ingested into Monarch'"
            design="small"
            color="secondary"
            icon="calendar-alt"
            :text="source.date"
          />
        </AppFlex>

        <!-- row of picture, description, and other summary info -->
        <img
          v-if="source.image"
          class="image"
          :src="source.image"
          :alt="source.name"
        />
        <p v-if="source.description" v-html="source.description" />
        <AppMarkdown v-if="source.usage" :source="source.usage" component="p" />

        <!-- row of file download links -->
        <p v-if="source.files?.length">
          <strong>Ingested Files:</strong>
        </p>
        <div v-if="source.files?.length" class="files">
          <AppLink
            v-for="(file, fileIndex) in source.files"
            :key="fileIndex"
            v-tooltip="breakUrl(file)"
            :to="file"
            class="truncate"
          >
            {{ getFilename(file) }}
          </AppLink>
        </div>
      </AppAccordion>
    </AppFlex>
  </AppSection>

  <!-- all downloads -->
  <AppSection>
    <p>
      A listing of all data that Monarch archives for use in its knowledge graph
      and tools:
    </p>
    <AppButton
      icon="download"
      text="All Downloads"
      to="https://archive.monarchinitiative.org/latest/"
    />
  </AppSection>

  <!-- notes -->
  <AppSection>
    <AppHeading>Note about licensing</AppHeading>
    <p>
      Each of these sources has its own license. We have described this
      licensing challenge extensively on
      <AppLink to="https://reusabledata.org/">reusabledata.org</AppLink> and our
      <AppLink to="https://doi.org/10.1371/journal.pone.0213090"
        >2018 PlosOne publication</AppLink
      >. Many of the specific data resources we use in Monarch have been
      evaluated according to our reusabledata.org rubric; see the
      <AppLink to="https://reusabledata.org/#our-sources-data"
        >corpus of evaluations here</AppLink
      >.
    </p>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { getDatasets } from "@/api/datasets";
import { getOntologies } from "@/api/ontologies";
import type { Source } from "@/api/source";
import AppAccordion from "@/components/AppAccordion.vue";
import AppCheckbox from "@/components/AppCheckbox.vue";
import { useQuery } from "@/util/composables";
import { breakUrl } from "@/util/string";

/** whether to show dataset sources */
const showDatasets = ref(true);
/** whether to show ontology sources */
const showOntologies = ref(true);

/** get filename from full path */
function getFilename(path = "") {
  return path
    .split("/")
    .filter((part) => part)
    .pop();
}

const {
  query: getSources,
  data: sources,
  isLoading,
  isError,
} = useQuery(async function () {
  /** get sources from apis */
  const datasets = await getDatasets();
  const ontologies = await getOntologies();

  /** combine sources */
  const sources = [...datasets, ...ontologies];

  /** sort sources alphabetically by name or id */
  sources.sort((a: Source, b: Source) => {
    if (
      (a?.name || a?.id || "").toLowerCase() <
      (b?.name || b?.id || "").toLowerCase()
    )
      return -1;
    else return 1;
  });

  /** import images */
  for (const source of sources) {
    try {
      if (!source.image) {
        source.image = "";
        continue;
      }
      if (source.image?.startsWith("http")) continue;
      source.image = (
        await import(`../../assets/sources/${source.image}.png`)
      ).default;
    } catch (error) {
      console.error("couldn't load source image", error);
    }
  }

  return sources;
}, []);

onMounted(getSources);

/** shown sources */
const filteredSources = computed((): Source[] =>
  sources.value.filter(
    (source: Source) =>
      (source.type === "dataset" && showDatasets.value) ||
      (source.type === "ontology" && showOntologies.value)
  )
);

/** number of dataset sources */
const datasetCount = computed(
  (): number =>
    sources.value.filter((source) => source.type === "dataset").length
);

/** number of ontology sources */
const ontologyCount = computed(
  (): number =>
    sources.value.filter((source) => source.type === "ontology").length
);
</script>

<style lang="scss" scoped>
.image {
  max-width: min(100%, 200px);
  max-height: 100px;
  margin: 10px auto;
}

.files {
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr 1fr;
  justify-items: flex-start;
  text-align: left;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
}
</style>
