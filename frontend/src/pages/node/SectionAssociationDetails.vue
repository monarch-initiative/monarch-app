<!--
  node page association details section, viewer for supporting evidence of an 
  association
-->

<template>
  <AppSection>
    <AppHeading icon="flask">Association Details</AppHeading>

    <div>
      Details for the selected association, <br />
      <AppNodeBadge
        :node="{
          id: association.subject,
          name: association.subject_label,
          category: association.subject_category,
          info: association.subject_taxon_label,
        }"
      />&nbsp; <AppPredicateBadge :association="association" />&nbsp;
      <AppNodeBadge
        :node="{
          id: association.object,
          name: association.object_label,
          category: association.object_category,
          info: association.object_taxon_label,
        }"
      />
    </div>

    <AppDetails>
      <AppDetail
        title="Evidence Codes"
        :count="association.evidence_count"
        icon="flask"
        :full="true"
      >
        <AppFlex gap="small" align-h="left">
          <span
            v-for="(source, index) in association.has_evidence"
            :key="index"
            >{{ source }}</span
          >
        </AppFlex>
      </AppDetail>

      <AppDetail title="Primary Knowledge Source" icon="lightbulb">
        <span>{{ association.primary_knowledge_source }}</span>
      </AppDetail>

      <AppDetail title="Provided By" icon="notes-medical">
        <AppLink :to="association.provided_by_link?.url || ''">
          {{ association.provided_by_link?.id || association.provided_by }}
        </AppLink>
      </AppDetail>

      <AppDetail
        title="Publications"
        :count="association.publications?.length"
        icon="book"
        :full="true"
      >
        <AppFlex gap="small" align-h="left">
          <span
            v-for="(publication, index) of association.publications"
            :key="index"
          >
            {{ publication }}
          </span>
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import type { DirectionalAssociation, Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import { scrollToElement } from "@/router";
import { waitFor } from "@/util/dom";

type Props = {
  /** current node */
  node: Node;
  /** selected association */
  association: DirectionalAssociation;
};

const props = defineProps<Props>();

/** scroll details section into view */
async function scrollIntoView() {
  scrollToElement(await waitFor("#association-details"));
}

watch(() => props.association, scrollIntoView);
onMounted(scrollIntoView);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
</style>
