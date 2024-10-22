<!--
  node page extra info section. more detailed metadata/info about node.
-->

<template>
  <AppSection width="full" alignment="left" class="inset">
    <AppHeading icon="clipboard-list">Extra Info</AppHeading>

    <AppDetails>
      <!-- source documentation -->
      <AppDetail :blank="!node.provided_by_link" title="Source Documentation">
        <AppLink :to="node.provided_by_link?.url || ''">
          {{ node.provided_by_link?.id || node.provided_by }}
        </AppLink>
      </AppDetail>

      <!-- external references -->
      <AppDetail
        :blank="!node.external_links?.length"
        title="External References"
        :full="true"
      >
        <AppFlex align-h="left" gap="small">
          <AppLink
            v-for="(link, index) of node.external_links"
            :key="index"
            :to="link.url || ''"
            >{{ link.id }}</AppLink
          >
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import type { Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();
</script>
