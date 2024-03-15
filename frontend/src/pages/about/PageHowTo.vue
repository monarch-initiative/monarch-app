<!-- 
  how to
 -->

<template>
  <AppSection v-show="false">
    <AppHeading>How to use Monarch Intiative</AppHeading>
    <p>
      The Monarch Initiative is an extensive knowledge graph and ecosystem of
      tools made for the benefit of clinicians, researchers, and scientists.
      This section is intended to help you get started in using these tools.
      Advanced users may want to head directly to the
      <AppLink
        to="https://github.com/obophenotype/upheno/wiki/Phenotype-Ontologies-Reconciliation-Effort"
        >home page</AppLink
      >
      and start exploring on your own.
    </p>
  </AppSection>

  <AppSection>
    <AppHeading>What do you want to do with Monarch to do today?</AppHeading>
    <p>
      The Monarch Initiative is an extensive knowledge graph and ecosystem of
      tools made for the benefit of clinicians, researchers, and scientists.
    </p>
    <AppAccordion text="Search and use information about a gene, disease, or phenotype..." >
      <TabSearch :minimal="true" />
    </AppAccordion>
    <AppButton
      to="https://obophenotype.github.io/upheno/"
      text="Search and use information about a gene, disease, or phenotype..."
      icon="arrow-right"
    />
    <AppButton
      to="https://obophenotype.github.io/upheno/"
      text="Find similar diseases based on a phenotypes or symptoms..."
      icon="arrow-right"
    />
    <AppAccordion text="Find similar diseases based on a phenotypes or symptoms..." >
      <TabSearch />
    </AppAccordion>
    <AppButton
      to="https://obophenotype.github.io/upheno/"
      text="Annotate a patients symptoms to terms in the Monarch KG..."
      icon="arrow-right"
    />
    <AppButton
      to="https://obophenotype.github.io/upheno/"
      text="Compare phenotypes between two diseases or genes..."
      icon="arrow-right"
    />
    <AppButton
      to="https://obophenotype.github.io/upheno/"
      text="Find additional information about..."
      icon="arrow-right"
    />
  </AppSection>

  <AppSection design="fill">
    <AppHeading>Goals</AppHeading>
  </AppSection>

  <AppSection>
    <AppHeading>
      <AppIcon icon="resource-upheno" />
      Heading
    </AppHeading>

    <p>
      Info
      <AppLink
        to="https://github.com/obophenotype/upheno/wiki/Phenotype-Ontologies-Reconciliation-Effort"
        >Phenotype Ontologies Reconciliation Effort</AppLink
      >.
    </p>
    <AppButton
      to="https://obophenotype.github.io/upheno/"
      text="Let's make this button text really really long to see how it looks, that wasn't nearly long enough... I need to make this a super large amount of text. Now how does it look?"
      icon="arrow-right"
    />
  </AppSection>
</template>

<script setup lang="ts">
import AppAccordion from '@/components/AppAccordion.vue'
import TabSearch from '../explore/TabSearch.vue'

export default {
  data() {
    return {
      minimal: true
    };
  },
  methods: {
    toggleMinimal() {
      this.minimal = !this.minimal;
    }
  }
};
</script>
