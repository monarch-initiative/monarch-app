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
      <AppPredicateBadge :association="association" />&nbsp;
      <AppNodeBadge
        :node="{
          id: association.subject,
          name: association.subject_label,
          category: association.subject_category,
        }"
      />
    </div>

    <AppDetails>
      <AppDetail
        title="Evidence Codes"
        :count="association.evidence_count"
        icon="flask"
        :big="true"
      >
        <AppFlex gap="small" h-align="left">
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
        :big="true"
      >
        <AppFlex gap="small" h-align="left">
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

/** scroll evidence section into view */
async function scrollIntoView() {
  scrollToElement(await waitFor("#evidence"));
}

watch(() => props.association, scrollIntoView);
onMounted(scrollIntoView);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
</style>
