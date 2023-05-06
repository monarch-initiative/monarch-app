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
        <template #subject="{ cell }: { cell: Evidence['subject'] }">
          <AppNodeBadge :node="cell" />
        </template>

        <!-- relation -->
        <template #relation="{ cell }: { cell: Evidence['relation'] }">
          <AppRelationBadge :relation="cell" />
        </template>

        <!-- "object" -->
        <template #object="{ cell }: { cell: Evidence['object'] }">
          <AppNodeBadge :node="cell" />
        </template>

        <!-- evidence codes -->
        <template #codes="{ cell }: { cell: Evidence['codes'] }">
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
        <template #publications="{ cell }: { cell: Evidence['publications'] }">
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
        <template #sources="{ cell }: { cell: Evidence['sources'] }">
          <AppLink
            v-for="(code, index) in cell"
            :key="index"
            :to="code.link"
            :no-icon="true"
            >{{ code.name }}</AppLink
          >
        </template>

        <!-- references -->
        <template #references="{ cell }: { cell: Evidence['references'] }">
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
import { onMounted, ref, watch } from "vue";
import type { Evidence } from "@/api/association-evidence";
import { getAssociationEvidence } from "@/api/association-evidence";
import type { Node } from "@/api/model";
import type { Association } from "@/api/node-associations";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppRelationBadge from "@/components/AppRelationBadge.vue";
import type { Cols } from "@/components/AppTable.vue";
import AppTable from "@/components/AppTable.vue";
import AppTabs from "@/components/AppTabs.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { appendToBody } from "@/global/tooltip";
import { scrollToElement } from "@/router";
import { useQuery } from "@/util/composables";
import { waitFor } from "@/util/dom";
import { downloadJson } from "@/util/download";
import { breakUrl } from "@/util/string";

type Props = {
  /** current node */
  node: Node;
  /** selected association id */
  selectedAssociation: Association;
};

const props = defineProps<Props>();

/** mode tabs */
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

/** table columns */
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

/** get evidence data */
const {
  query: getEvidence,
  data: evidence,
  isLoading,
  isError,
} = useQuery(
  async function () {
    /** scroll to evidence section */
    waitFor("#evidence", scrollToElement);

    /** get evidence data */
    const response = await getAssociationEvidence(
      props.selectedAssociation?.id
    );

    return response;
  },

  /** default value */
  { summary: { codes: [], publications: [], sources: [] }, table: [] }
);

/** download table data */
async function download() {
  /** warn user */
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
