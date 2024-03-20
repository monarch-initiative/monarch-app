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
    <p>Phenotype Profile Search from v2 website</p>
    <AppAccordion text="Phenotype Profile Search" >
      <p>This Phenotype Profile Search enables you to find phenotypically similar diseases or
        genes in a variety of organisms, then visualize their overlap. Begin by constructing
        a "profile" (a collection of phenotypes) then create a comparison profile.
      </p>
      <AppAccordion text="1.  Create a Profile of Phenotypes">
        <AppAccordion text="I have a phenotype list I can paste." >
          <TabPhenotypeExplorer :minimal="true" />
        </AppAccordion>
        <AppAccordion text="I need some help to create a phenotype profile." >
          <p>I want to generate a phenotype profile from a ...</p>
          <AppAccordion text="gene." >
            <TabSearch :minimal="true" />
          </AppAccordion>
          <AppAccordion text="disease." >
            <TabSearch :minimal="true" />
          </AppAccordion>
        </AppAccordion>
      </AppAccordion>
      <AppAccordion text="2. What do you want to compare against?">
        <AppAccordion text="Show me everything" >
          <AppButton to="" text="all matching genes." icon="arrow-right" />
          <AppButton to="" text="all matching diseases." icon="arrow-right" />
        </AppAccordion>
        <AppAccordion text="I know what I want to compare." >
          <AppButton to="" text="A specific gene" icon="arrow-right" />
          <AppButton to="" text="A specific disease" icon="arrow-right" />
          <AppButton to="" text="I will paste a list of phenotypes" icon="arrow-right" />
        </AppAccordion>
      </AppAccordion>
    </AppAccordion>
  </AppSection>

  <AppSection>
    <p>How To example layout 1</p>
    <AppHeading>What do you want to do with Monarch today?</AppHeading>
    <p>
      The Monarch Initiative is an extensive knowledge graph and ecosystem of
      tools made for the benefit of clinicians, researchers, and scientists.
    </p>
    
    <AppButton
      color="secondary"
      to="explore#search"
      text="Search and use information about a gene, disease, or phenotype..."
      icon="arrow-right"
    />
    <AppButton
      color="secondary"
      to="explore#text-annotator"
      text="Annotate a patients symptoms to terms in the Monarch KG..."
      icon="arrow-right"
    />
    <AppButton
      color="secondary"
      to="explore#phenotype-explorer"
      text="Find similar diseases based on a phenotypes or symptoms..."
      icon="arrow-right"
    />
    <AppButton
      color="secondary"
      to="explore#phenotype-explorer"
      text="Compare phenotypes between two diseases or genes..."
      icon="arrow-right"
    />
    <AppButton
      color="secondary"
      to="about"
      text="Find additional information about..."
      icon="arrow-right"
    />
  </AppSection>

  <AppSection>
    <p>How To example layout 2</p>
    <AppHeading>What do you want to do with Monarch today?</AppHeading>
    <p>
      The Monarch Initiative is an extensive knowledge graph and ecosystem of
      tools made for the benefit of clinicians, researchers, and scientists.
    </p>
    
    <AppAccordion text="Search and use information about a gene, disease, or phenotype..." >
      <TabSearch :minimal="true" />
    </AppAccordion>
    <AppAccordion text="Annotate a patients symptoms to terms in the Monarch KG..." >
      <TabTextAnnotator :minimal="true" />
    </AppAccordion>
    <AppAccordion text="Find similar diseases based on a phenotypes or symptoms..." >
      <TabPhenotypeExplorer :minimal="true" />
    </AppAccordion>
    <AppAccordion text="Compare phenotypes between two diseases or genes..." >
      <TabPhenotypeExplorer :minimal="true" />
    </AppAccordion>
    <AppAccordion text="Find additional information about..." >
      <TabSearch />
    </AppAccordion>
  </AppSection>

  <AppSection>
    <p>How To example layout 3</p>
    <AppSelectSingle
      v-model="selectedOption"
      name="Sort"
      :options="selectOptions"
    />
  </AppSection>

  <AppSection>
    <p>From here below is just some extra things that might be interesting to dress up the page if we want.</p>
  </AppSection>

  <AppSection design="fill">
    <AppHeading>Goals</AppHeading>
  </AppSection>

  <AppSection>
    <AppHeading icon="resource-upheno">
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
import { ref } from "vue"
// import { computed, nextTick, ref, watch } from "vue"
import AppAccordion from '@/components/AppAccordion.vue'
import TabSearch from '../explore/TabSearch.vue'
import TabTextAnnotator from "../explore/TabTextAnnotator.vue"
import TabPhenotypeExplorer from '../explore/TabPhenotypeExplorer.vue'
// import AppSelectSingle from "@/components/AppSelectSingle.vue"
import AppSelectSingle, { type Option } from "@/components/AppSelectSingle.vue"


const selectOptions: Option[] = [
  { id: "none_selected", label: "What do you want to do with Monarch today?" },
  { id: "tabsearch", label: "Search and use information about a gene, disease, or phenotype..." },
  { id: "alpha", label: "Find similar diseases based on a phenotypes or symptoms..." },
  { id: "alpha-rev", label: "Annotate a patients symptoms to terms in the Monarch KG..." },
  { id: "total", label: "Compare phenotypes between two diseases or genes..." },
  { id: "total-rev", label: "Find additional information about..." },
];
const selectedOption = ref(selectOptions[0])

</script>
