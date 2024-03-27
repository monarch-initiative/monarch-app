<!-- 
  how to
 -->

<template>
  <AppSection v-show="true">
    <AppHeading>How to use Monarch Intiative</AppHeading>
    <p>
      The Monarch Initiative is an extensive knowledge graph and ecosystem of
      tools made for the benefit of clinicians, researchers, and scientists.
      This section is intended to help you get started in using these tools.
    </p>
  </AppSection>

  <AppSection design="fill">
    <AppHeading>Example from previous site</AppHeading>
    <AppHeading :level="4"
      >Content exact from site but layout is not.</AppHeading
    >
  </AppSection>

  <AppSection>
    <p>Phenotype Profile Search from v2 website</p>
    <AppAccordion text="Phenotype Profile Search">
      <p>
        This Phenotype Profile Search enables you to find phenotypically similar
        diseases or genes in a variety of organisms, then visualize their
        overlap. Begin by constructing a "profile" (a collection of phenotypes)
        then create a comparison profile.
      </p>
      <AppAccordion text="1.  Create a Profile of Phenotypes">
        <AppAccordion text="I have a phenotype list I can paste.">
          <TabPhenotypeExplorer :minimal="true" />
        </AppAccordion>
        <AppAccordion text="I need some help to create a phenotype profile.">
          <p>I want to generate a phenotype profile from a ...</p>
          <AppAccordion text="gene.">
            <TabSearch :minimal="true" />
          </AppAccordion>
          <AppAccordion text="disease.">
            <TabSearch :minimal="true" />
          </AppAccordion>
        </AppAccordion>
      </AppAccordion>
      <AppAccordion text="2. What do you want to compare against?">
        <AppAccordion text="Show me everything">
          <AppButton to="" text="all matching genes." icon="arrow-right" />
          <AppButton to="" text="all matching diseases." icon="arrow-right" />
        </AppAccordion>
        <AppAccordion text="I know what I want to compare.">
          <AppButton to="" text="A specific gene" icon="arrow-right" />
          <AppButton to="" text="A specific disease" icon="arrow-right" />
          <AppButton
            to=""
            text="I will paste a list of phenotypes"
            icon="arrow-right"
          />
        </AppAccordion>
      </AppAccordion>
    </AppAccordion>
  </AppSection>

  <AppSection design="fill">
    <AppHeading>Candidate layouts for new How-To</AppHeading>
    <AppHeading :level="4">Content isn't complete in all layouts.</AppHeading>
  </AppSection>

  <AppSection>
    <p>How To candidate layout 1</p>
    <AppHeading>Would you like some help?</AppHeading>
    <AppSelectSingle
      v-model="selectedOption"
      name="Sort"
      :options="selectOptions"
    />
    <div v-if="selectedOption.id === 'search'">
      <AppHeading>
        Searching for a single gene, disease, or phenotype.
      </AppHeading>
      <p>
        The search bar in the page header allows flexible searching of gene,
        disease, or phenotype all in one place.
      </p>
      <AppHighlight :src="search">
        <ul>
          <li>Genes can be searched by common gene, gene ID, or symbol.</li>
          <li>Diseases can be searched by name or ID.</li>
          <li>Phenotypes can be searched by name or ID.</li>
        </ul>
      </AppHighlight>
      <p>
        Any of these descriptors can be entered into the search bar directly.
        Press enter or select a suggestion to search.
      </p>
      <AppButton
        to="explore#search"
        text="Take me to search..."
        icon="arrow-right"
      />
    </div>
    <div v-if="selectedOption.id === 'textAnnotator'">
      <AppHeading> Annotating text with terms from the Monarch KG. </AppHeading>
      <p>
        Annotate a descriptive text containing symptoms or phenotypes with terms
        from the Monarch KG.
      </p>
      <AppHighlight :src="textAnnotator">
        <ul>
          <li>
            Paste or upload the text containing symptoms or phenotypes in the
            text box.
          </li>
          <li>Click the "Annotate" button.</li>
          <li>
            The results will contain your free text with matching terms replaced
            with Monarch terms.
          </li>
        </ul>
      </AppHighlight>
      <AppButton
        to="explore#text-annotator"
        text="Take me to text annotator..."
        icon="arrow-right"
      />
    </div>
    <div v-if="selectedOption.id === 'phenotypeExplorer'">
      <AppHeading>
        Compare phenotype profiles of genese or diseases or your own phenotype
        profiles.
      </AppHeading>
      <p>
        Use the phenotype explorer to find similar genes or diseases based on
        phenotypes or compare phenotype profiles.
      </p>
      <AppHighlight :src="phenotypeExplorer">
        <ul>
          <li>
            Enter the name of a disease or a list of phenotypes in the top
            search bar
          </li>
          <li>
            Enter another disease, gene, or list of phenotypes you want to
            compare to
          </li>
          <li>Click the "Search" button</li>
          <li>
            The results will contain diseases that match the phenotypes or
            symptoms you entered.
          </li>
        </ul>
      </AppHighlight>
      <AppButton
        to="explore#phenotype-explorer"
        text="Take me to phenotype explorer..."
        icon="arrow-right"
      />
    </div>
  </AppSection>

  <AppSection>
    <p>How To candidate layout 2</p>
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
    <p>How To candidate layout 3</p>
    <AppHeading>What do you want to do with Monarch today?</AppHeading>
    <p>
      The Monarch Initiative is an extensive knowledge graph and ecosystem of
      tools made for the benefit of clinicians, researchers, and scientists.
    </p>

    <AppAccordion
      text="Search and use information about a gene, disease, or phenotype..."
    >
      <TabSearch :minimal="true" />
    </AppAccordion>
    <AppAccordion
      text="Annotate a patients symptoms to terms in the Monarch KG..."
    >
      <TabTextAnnotator :minimal="true" />
    </AppAccordion>
    <AppAccordion
      text="Find similar diseases based on a phenotypes or symptoms..."
    >
      <TabPhenotypeExplorer :minimal="true" />
    </AppAccordion>
    <AppAccordion text="Compare phenotypes between two diseases or genes...">
      <TabPhenotypeExplorer :minimal="true" />
    </AppAccordion>
    <AppAccordion text="Find additional information about...">
      <TabSearch />
    </AppAccordion>
  </AppSection>

  <AppSection>
    <p>
      From here below is just some extra things that might be interesting to
      dress up the page if we want.
    </p>
  </AppSection>

  <AppSection>
    <AppHeading>Test Highlights</AppHeading>
    <AppHighlight :src="search">
      Quickly and easily browse nodes. Filter by category and taxon. See your
      recent and frequent searches.
    </AppHighlight>
  </AppSection>

  <AppSection design="fill">
    <AppHeading>Goals</AppHeading>
  </AppSection>

  <AppSection>
    <AppHeading icon="resource-upheno"> Heading </AppHeading>

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
import { ref } from "vue";
import phenotypeExplorer from "@/assets/demos/phenotype-explorer.mp4";
import search from "@/assets/demos/search.mp4";
import textAnnotator from "@/assets/demos/text-annotator.mp4";
// import { computed, nextTick, ref, watch } from "vue"
import AppAccordion from "@/components/AppAccordion.vue";
import AppHighlight from "@/components/AppHighlight.vue";
// import AppSelectSingle from "@/components/AppSelectSingle.vue"
import AppSelectSingle, { type Option } from "@/components/AppSelectSingle.vue";
import TabPhenotypeExplorer from "../explore/TabPhenotypeExplorer.vue";
import TabSearch from "../explore/TabSearch.vue";
import TabTextAnnotator from "../explore/TabTextAnnotator.vue";

const selectOptions: Option[] = [
  { id: "none_selected", label: "What do you want to do with Monarch today?" },
  {
    id: "search",
    label: "Search and use information about a gene, disease, or phenotype...",
  },
  {
    id: "textAnnotator",
    label: "Annotate a patients symptoms to terms in the Monarch KG...",
  },
  {
    id: "phenotypeExplorer",
    label: "Find similar diseases based on a phenotypes or symptoms...",
  },
  {
    id: "pheno_compare",
    label: "Compare phenotypes between two diseases or genes...",
  },
  { id: "about", label: "Find additional information about..." },
];
const selectedOption = ref(selectOptions[0]);
</script>
