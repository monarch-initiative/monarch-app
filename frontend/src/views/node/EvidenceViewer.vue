<!--
  node page associations section, viewer for supporting evidence of an 
  association 
-->

<template>
  <AppSection>
    <AppHeading icon="flask">Evidence</AppHeading>

    <div>
      Evidence for the selected association, <br />
      <AppNodeBadge :node="node" />&nbsp;
      <AppRelationBadge :relation="selectedAssociation.relation" />&nbsp;
      <AppNodeBadge :node="selectedAssociation.object" />
    </div>

    <!-- status -->
    <AppStatus v-if="isLoading" code="loading">Loading evidence</AppStatus>
    <AppStatus v-else-if="isError" code="error"
      >Error loading evidence</AppStatus
    >

    <!-- evidence tabs -->
    <AppTabs
      v-else
      v-model="tab"
      :tabs="tabs"
      name="Evidence viewing mode"
      :url="false"
    />

    <!-- summary mode -->
    <template v-if="tab === 'summary' && evidence.summary">
      <AppDetails>
        <AppDetail
          :title="`Evidence Codes`"
          :count="evidence.summary?.codes.length"
          icon="flask"
        >
          <AppLink
            v-for="(code, index) in evidence.summary?.codes"
            :key="index"
            :to="code.link"
            >{{ code.name }}</AppLink
          >
        </AppDetail>

        <AppDetail
          :title="`Sources`"
          :count="evidence.summary?.sources.length"
          icon="database"
        >
          <AppLink
            v-for="(source, index) in evidence.summary?.sources"
            :key="index"
            :to="source"
            v-html="breakUrl(source)"
          />
        </AppDetail>

        <AppDetail
          :title="`Publications`"
          :count="evidence.summary?.publications.length"
          icon="book"
        >
          <AppFlex gap="small" h-align="left">
            <AppLink
              v-for="(publication, index) in evidence.summary?.publications"
              :key="index"
              :to="publication.link"
              >{{ publication.name }}</AppLink
            >
          </AppFlex>
        </AppDetail>
      </AppDetails>
    </template>

    <!-- table mode -->
    <template v-if="tab === 'table' && evidence.table?.length">
      <AppTable
        :cols="cols"
        :rows="evidence.table || []"
        :start="0"
        :total="evidence.table?.length || 0"
        :show-controls="false"
        @download="download"
      >
        <!-- "subject" -->
        <template #subject="{ cell }">
          <AppNodeBadge :node="cell" />
        </template>

        <!-- relation -->
        <template #relation="{ cell }">
          <AppRelationBadge :relation="cell" />
        </template>

        <!-- "object" -->
        <template #object="{ cell }">
          <AppNodeBadge :node="cell" />
        </template>

        <!-- evidence codes -->
        <template #codes="{ cell }">
          <AppFlex direction="col" gap="small" h-align="left">
            <AppLink
              v-for="(code, index) in cell"
              :key="index"
              :to="code.link"
              :no-icon="true"
              >{{ code.name }}</AppLink
            >
          </AppFlex>
        </template>

        <!-- publications -->
        <template #publications="{ cell }">
          <AppFlex direction="col" gap="small" h-align="left">
            <AppLink
              v-for="(publication, index) in cell.slice(0, 1)"
              :key="index"
              :to="publication.link"
              :no-icon="true"
              >{{ publication.name }}</AppLink
            >
            <template v-if="cell.length > 1">
              <tooltip :interactive="true" :append-to="appendToBody">
                <span>and {{ cell.length - 1 }} more...</span>
                <template #content>
                  <AppFlex h-align="left" gap="tiny">
                    <AppLink
                      v-for="(publication, index) in cell.slice(1)"
                      :key="index"
                      :to="publication.link"
                      >{{ publication.name }}</AppLink
                    >
                  </AppFlex>
                </template>
              </tooltip>
            </template>
          </AppFlex>
        </template>

        <!-- sources -->
        <template #sources="{ cell }">
          <AppLink
            v-for="(code, index) in cell"
            :key="index"
            :to="code.link"
            :no-icon="true"
            >{{ code.name }}</AppLink
          >
        </template>

        <!-- references -->
        <template #references="{ cell }">
          <AppLink
            v-for="(code, index) in cell"
            :key="index"
            :to="code.link"
            :no-icon="true"
            >{{ code.name }}</AppLink
          >
        </template>
      </AppTable>
    </template>
  </AppSection>
</template>

<script setup lang="ts">
import { watch, onMounted, ref } from "vue";
import AppTabs from "@/components/AppTabs.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppDetail from "@/components/AppDetail.vue";
import AppTable from "@/components/AppTable.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppRelationBadge from "@/components/AppRelationBadge.vue";
import type { Node } from "@/api/node-lookup";
import { scrollToElement } from "@/router";
import { getAssociationEvidence } from "@/api/association-evidence";
import { breakUrl } from "@/util/string";
import { appendToBody } from "@/global/tooltip";
import { waitFor } from "@/util/dom";
import type { Association } from "@/api/node-associations";
import { useQuery } from "@/util/composables";
import { snackbar } from "@/components/TheSnackbar.vue";
import { downloadJson } from "@/util/download";
import type { Cols } from "@/components/AppTable.vue";

type Props = {
  /** Current node */
  node: Node;
  /** Selected association id */
  selectedAssociation: Association;
};

const props = defineProps<Props>();

/** Mode tabs */
const tabs = [
  {
    id: "summary",
    text: "Summary",
    icon: "clipboard",
    tooltip: "High-level overview of evidence",
  },
  {
    id: "table",
    text: "Table",
    icon: "table",
    tooltip: "All evidence data, in tabular form",
  },
];
const tab = ref(tabs[0].id);

/** Table columns */
const cols: Cols = [
  {
    id: "subject",
    key: "subject",
    heading: "Subject",
    width: "max-content",
  },
  {
    id: "relation",
    key: "relation",
    heading: "Relation",
    width: "max-content",
  },
  {
    id: "object",
    key: "object",
    heading: "Object",
    width: "max-content",
  },
  {
    id: "codes",
    key: "codes",
    heading: "Evidence Codes",
    width: "max-content",
  },
  {
    id: "publications",
    key: "publications",
    heading: "Publications",
    width: "max-content",
  },
  {
    id: "sources",
    key: "sources",
    heading: "Sources",
  },
  {
    id: "references",
    key: "references",
    heading: "References",
  },
];

/** Get evidence data */
const {
  query: getEvidence,
  data: evidence,
  isLoading,
  isError,
} = useQuery(
  async function () {
    /** Scroll to evidence section */
    waitFor("#evidence", scrollToElement);

    /** Get evidence data */
    const response = await getAssociationEvidence(
      props.selectedAssociation?.id
    );

    return response;
  },

  /** Default value */
  { summary: { codes: [], publications: [], sources: [] }, table: [] }
);

/** Download table data */
async function download() {
  /** Warn user */
  snackbar(
    `Downloading data for ${evidence.value.table.length} table entries.`
  );

  downloadJson(evidence.value.table);
}

onMounted(getEvidence);
watch(() => props.selectedAssociation, getEvidence);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
</style>
