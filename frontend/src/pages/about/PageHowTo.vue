<!-- 
  how to
 -->

<template>
  <AppSection v-show="true">
    <AppHeading>How to use Monarch Intiative</AppHeading>
    <p>
      The Monarch Initiative is an extensive, cross-species, semantic knowledge graph and ecosystem of
      tools made for the benefit of informaticians, clinicians, researchers, patients, and more.
      This section will help you quickly and easily explore the graph on the website, with the API,
      or using the ecosystem of related tools.
    </p>
  </AppSection>

  <AppSection>
    <AppHeading>What do you want to do with Monarch today?</AppHeading>
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
          <li>Genes can be searched by common gene name, gene ID, or symbol.</li>
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
        Compare phenotype profiles.
      </AppHeading>
      <p>
        Find similar genes or diseases based on phenotypes using the phenotype explorer.
        You can also use phenotype explorer to compare two phenotype profiles of your own.
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
    <div v-if="selectedOption.id === 'monarchAPI'">
      <AppHeading>
        Using the Monarch API to integrate the KG into tools.
      </AppHeading>
      <p style="padding-bottom: 1.5rem;">
        Monarch provides a RESTful API to access the KG and related services.
        Here are some of the services built using the Monarch API you can use or to serve as a reference.
      </p>
      <AppTile
        to="http://api-v3.monarchinitiative.org/"
        icon="code"
        title="API"
        subtitle="The API serving this website"
      />
      <AppTile
        to="https://github.com/monarch-initiative/oai-monarch-plugin"
        icon="user-gear"
        title="ChatGPT Plugin"
        subtitle="Monarch KG with ChatGPT"
      />
      <AppTile
        to="https://github.com/monarch-initiative/monarchr"
        icon="R"
        title="R Package"
        subtitle="Monarch KG in R"
      />
      <p style="padding-top: 1.5rem;">
        Use the buttons above to go directly to the API documentation, the ChatGPT plugin, or the R package. Or see the further information below.
      </p>
      <ul>
        <li>
          Monarch provides a RESTful API which we use to develop the website and for other tools we provide.
          You are welcome to use the API for your own projects. For more information
          <AppLink to="http://api-v3.monarchinitiative.org/">see the API documentation</AppLink>.
        </li>
        <li>
          A ChatGPT plugin uses calls to the Monarch API to process casual language questions about genes, diseases, and phenotypes.
          The plugin uses the API to get information from the KG on identified terms. Responses are tailored to a more
          general audience and may be easier for non-experts to understand. For further reading please 
          <AppLink to="https://monarchinit.medium.com/knowledge-backed-ai-with-monarch-a-match-made-in-heaven-a8296eec6b9f">
            see the announcement paper
          </AppLink> or you can go straight to the 
          <AppLink to="https://github.com/monarch-initiative/oai-monarch-plugin">
            GitHub repository
          </AppLink>.
        </li>
        <li>
          The Monarch R package provides easy access, manipulation, and analysis of Monarch KG data resources from R.
          For more information please see the 
          <AppLink to="https://github.com/monarch-initiative/monarchr">
            MonarchR GitHub repository
          </AppLink>.
        </li>
      </ul>
    </div>
    <div v-if="selectedOption.id === 'about'">
      <AppHeading>
        More information about the Monarch Initiative.
      </AppHeading>
      <p style="padding-bottom: 1.5rem;">
        Here are some quick links for some of the most frequently requested information about the Monarch Initiative.
        For additional information, please see 
        <AppLink to="about">
          our about page
          </AppLink>.
      </p>
      <AppTile
        to="/cite"
        icon="feather-pointed"
        title="Cite"
        subtitle="How to cite and attribute Monarch"
      />
      <AppTile
        to="/overview"
        icon="cogs"
        title="Overview"
        subtitle="How all the pieces of Monarch fit together"
      />
      <AppTile
        to="/team"
        icon="users"
        title="Team"
        subtitle="The people behind Monarch"
      />
      <AppTile
        to="https://monarch-initiative.github.io/monarch-ingest/Sources"
        icon="database"
        title="Sources"
        subtitle="Datasets, ontologies, and downloads"
      />
      <p style="padding-top: 1.5rem;">
        Use the buttons above to go directly to the information listed. Additional information may be available on the about page.
      </p>
      <AppButton
        to="about"
        text="Take me to the full about page..."
        icon="arrow-right"
      />
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { ref } from "vue";
import phenotypeExplorer from "@/assets/demos/phenotype-explorer.mp4";
import search from "@/assets/demos/search.mp4";
import textAnnotator from "@/assets/demos/text-annotator.mp4";
import AppHighlight from "@/components/AppHighlight.vue";
import AppSelectSingle, { type Option } from "@/components/AppSelectSingle.vue";

const selectOptions: Option[] = [
  { id: "none_selected", label: "I want to..." },
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
    id: "monarchAPI",
    label: "Use the Monarch API with tools like ChatGPT/LLM or R...",
  },
  { id: "about", label: "Find additional information about..." },
];
const selectedOption = ref(selectOptions[0]);
</script>
