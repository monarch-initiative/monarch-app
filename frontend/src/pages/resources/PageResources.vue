<template>
  <AppSection>
    <AppHeading>Resources</AppHeading>
    <p>Resources and tools central to Monarch Initiative.</p>
    <p>
      The Monarch Initiative is an international consortium that leads key
      global standards and semantic data integration technologies. Monarch
      resources and integrated data are also foundational to many downstream
      applications and contexts; we work closely with a variety of stakeholders
      and resource-development communities to capture feedback and make
      improvements. To maximize utility and impact, the Monarch platform is
      composed of multiple open-source, open-access components. We promote
      provenance and transparency, enhanced use of standards and new
      technologies and improved data accessibility, end-user utility, and data
      submission. Below, we highlight a collection of our flagship projects.
      Learn more about the complete suite of Monarch resources on our
      organization's
      <AppLink to="https://monarch-initiative.github.io/monarch-documentation/">
        documentation pages
      </AppLink>
      .
    </p>
  </AppSection>
  <AppSection width="big">
    <AppHeading> Flagship Products </AppHeading>
    <AppGallery>
      <template v-for="category in resources" :key="category">
        <AppTile
          v-for="(resource, resourceIndex) in category"
          :key="resourceIndex"
          :to="resource.link"
          :icon="resource.icon"
          :title="resource.name"
          :subtitle="resource.description"
        />
      </template>
    </AppGallery>
  </AppSection>

  <AppSection>
    <AppHeading>AI and LLM</AppHeading>

    <p>
      The Monarch Initiative is developing a suite of AI tools to help
      researchers and clinicians make sense of the vast amount of data available
      in the Monarch ecosystem. These tools include machine learning models,
      embeddings, and other AI techniques to help with data integration, data
      analysis, and data interpretation.
    </p>
  </AppSection>

  <AppSection width="big">
    <AppHeading>Tools</AppHeading>
    <AppGallery>
      <AppTile
        v-for="(tool, toolIndex) in AiTools"
        :key="toolIndex"
        :to="tool.link"
        :icon="tool.icon"
        :title="tool.name"
        :subtitle="tool.description"
      />
    </AppGallery>
  </AppSection>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import resources from "./resources.json";

type AITool = {
  link: string;
  icon: string;
  name: string;
  description: string;
};

const AiTools: AITool[] = [
  {
    name: "Agent Smith",
    description: "A project to make it easy to instantiate AI agents that can safely and easily call APIs and locally defined functions to interact with the world. The Phenomics Assistant (formerly the Monarch Assistant) is an example of one such tool. ",
    link: "",
    icon: "",
  },
  {
    name: "CurateGPT",
    description: "A prototype web application and framework for performing general purpose AI-guided curation and curation-related operations over collections of objects. Uses DRAGONAI and RAG. Does not do grounding or mapping (just knows about JSON objects). Resources are stored in a ChromaDB vector database.",
    link: "",
    icon: "",
  },
  {
    name: "Datasette LLM library",
    description: "Or llm for short. A CLI utility and Python library for interacting with Large Language Models, both via remote APIs and models that can be installed and run on your own machine.",
    link: "",
    icon: "",
  },
  {
    name: "Langchain",
    description: "A framework for developing applications powered by language models. Supports connecting a language model to sources of context and enabling reasoning.",
    link: "",
    icon: "",
  },
  {
    name: "LinkML",
    description: "A modeling language and framework for describing, working with, and validating data in a variety of formats. OntoGPT uses LinkML to define extraction schemas.",
    link: "",
    icon: "",
  },
  {
    name: "Phenomics Assistant",
    description: "An AI chatbot with access to the Monarch Initiative biomedical knowledgebase. See demo at https://phenomics-assistant.streamlit.app/ ",
    link: "",
    icon: "",
  },
  {
    name: "OGER",
    description: "A flexible, dictionary-based system for extracting biomedical terms from scientific articles.",
    link: "",
    icon: "",
  },
  {
    name: "OntoGPT",
    description: "A tool for linking unstructured data to structured vocabularies with consistent identifiers. Uses SPIRES and TALISMAN methods.",
    link: "",
    icon: "",
  },
  {
    name: "Ontology Access Toolkit (OAK)",
    description: "Python library for common ontology operations over a variety of backends. OAK has its own TextAnnotator but it’s very simple. OntoGPT uses OAK for term retrieval, labeling, mapping, etc.",
    link: "",
    icon: "",
  },
  {
    name: "OntoRunner",
    description: "A wrapper for NER methods, intended for identifying ontology terms in text. Uses OGER and Spacy.",
    link: "",
    icon: "",
  },
  {
    name: "OpenAI Monarch Plugin for ChatGPT",
    description: "A plugin for querying the Monarch Knowledge Graph with ChatGPT. Requires premium account.",
    link: "",
    icon: "",
  },
];
</script>
