<!--
  text annotator tab on explore page

  input free/long text and finds references to nodes in monarch knowledge graph
-->

<template>
  <AppBreadcrumb />
  <PageTitle id="text-annotator" title="Text Annotator" />
  <AppSection>
    <AppTextbox
      v-model="content"
      :multi="true"
      icon="file-lines"
      placeholder="Paste full text"
      @change="onChange"
    />

    <!-- other options -->
    <AppFlex>
      <span>or</span>
      <AppUpload @upload="onUpload" />
      <span>or</span>
      <AppButton text="Try an example" design="small" @click="doExample()" />
    </AppFlex>

    <!-- submit button -->
    <AppButton text="Annotate Text" icon="search" @click="runAnnotateText" />
  </AppSection>

  <AppSection>
    <!-- status -->
    <AppStatus v-if="isLoading" code="loading">Loading annotations</AppStatus>
    <AppStatus v-if="isError" code="error">Error loading annotations</AppStatus>

    <!-- filename -->
    <strong v-if="annotations.length"
      >Annotations for {{ filename || "pasted text" }}</strong
    >

    <!-- results -->
    <p v-if="annotations.length" class="results">
      <tooltip
        v-for="({ text, tokens }, annotationIndex) in annotations"
        :key="annotationIndex"
        :interactive="true"
        :append-to="appendToBody"
        :tabindex="tokens.length ? 0 : -1"
        tag="span"
        >{{ text
        }}<template v-if="!!tokens.length" #content>
          <AppFlex direction="col" align-h="left" gap="tiny">
            <AppNodeBadge
              v-for="(token, index) in tokens"
              :key="index"
              :node="token"
              :show-id="true"
            />
          </AppFlex>
        </template>
      </tooltip>
    </p>

    <!-- actions -->
    <AppFlex v-if="annotations.length">
      <AppButton text="Download" icon="download" @click="download" />
      <AppButton
        v-tooltip="
          'Send any annotations above that are phenotypes to Phenotype Explorer for comparison'
        "
        to="search-phenotypes"
        :state="{ phenotypes: getPhenotypes() }"
        text="Phenotype Explorer"
        icon="arrow-right"
        color="secondary"
      />
    </AppFlex>
  </AppSection>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { uniqBy } from "lodash";
import { useLocalStorage } from "@vueuse/core";
import { annotateText } from "@/api/text-annotator";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppTextbox from "@/components/AppTextbox.vue";
import AppUpload from "@/components/AppUpload.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import { useQuery } from "@/composables/use-query";
import example from "@/data/text-annotator.json";
import { appendToBody } from "@/global/tooltip";
import { downloadJson } from "@/util/download";

/** text content */
const content = useLocalStorage("annotations-content", "");
/** file name of uploaded file (if applicable) */
const filename = useLocalStorage("annotations-filename", "");

/** annotation results */
const {
  query: runAnnotateText,
  data: annotations,
  isLoading,
  isError,
} = useQuery(async function () {
  return await annotateText(content.value);
}, []);

/** get text content and filename from upload button */
async function onUpload(data = "", file = "") {
  content.value = data;
  filename.value = file;
  await runAnnotateText();
}

/** on textbox change */
function onChange() {
  filename.value = "";
}

/** example full text */
async function doExample() {
  content.value = example.content;
  filename.value = "Example";
  await runAnnotateText();
}

/** download annotations */
function download() {
  downloadJson(
    annotations.value.filter(({ tokens }) => tokens.length),
    "annotations",
  );
}

/** get phenotype annotations to send to phenotype explorer */
function getPhenotypes() {
  /** gather annotations that are phenotypes */

  const phenotypes = [];
  for (const { tokens } of annotations.value)
    for (const { id, name } of tokens)
      if (id?.startsWith("HP:")) phenotypes.push({ id, name });

  /** de-duplicate, and send them to phenotype explorer component via router */
  return uniqBy(phenotypes, "id");
}

/** run annotations on mount if content loaded from storage */
onMounted(async () => {
  if (content.value) await runAnnotateText();
});
</script>

<style lang="scss" scoped>
.results {
  white-space: pre-line;
}
</style>
