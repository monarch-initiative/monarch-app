<template>
  <AppBreadcrumb />
  <PageTitle id="kg-about" title="About the Knowledge Graph" />
  <p class="tagline">
    Discover the power of our Knowledge Graph, seamlessly connecting biological
    data to reveal hidden relationships.
  </p>
  <!-- What is KG -->
  <AppSection width="big" class="kg-about">
    <AppHeading class="fullWidthHeader">
      What is Monarch Initiative Knowledge Graph?
    </AppHeading>

    <div class="content-container">
      <div class="text-column">
        <p>
          The Monarch Knowledge Graph (KG) comprises the combined knowledge of
          33 biomedical resources and biomedical ontologies, and is updated with
          the latest data from each source once a month. The components of the
          Monarch KG and the associations between them are represented as nodes,
          edges, and labels. A data source ingest imports data from resources
          such as the external Panther Database or Monarch’s disease annotations
          to Human Phenotype Ontology terms (HPOA) and transforms them into the
          Monarch KG schema. Ontologies are integrated into a ‘semantic layer,’
          a Biolink-conformant representation of the Phenomics Integrated
          Ontology (PHENIO), which serves as a hierarchical schema and
          classification system for the integrated data.
          <a
            href="https://academic.oup.com/nar/article/52/D1/D938/7449493?login=false"
            target="_blank"
            rel="noopener noreferrer"
            class="link"
          >
            Learn more
          </a>
        </p>
      </div>
      <iframe
        title="What is KnowledgeGraph?"
        class="video"
        src="https://www.youtube.com/embed/z11xZKBEO-U"
        frameborder="0"
        allow="autoplay; picture-in-picture"
        allowfullscreen
      ></iframe>
    </div>
  </AppSection>

  <!-- Entity and Association statistics -->
  <AppSection width="big">
    <div class="enity-association">
      <AppHeading>Entity and Association Statistics</AppHeading>
      <AppGallery :cols="4">
        <AppTile
          v-for="(item, index) in metadata.node"
          :key="index"
          :icon="item.icon"
          :title="startCase(item.label.replace(/biolink:/g, ''))"
          :subtitle="formatNumber(item.count, true)"
          design="small"
        />
        <AppTile
          v-for="(item, index) in metadata.association"
          :key="index"
          :icon="item.icon2 ? undefined : item.icon"
          :title="startCase(item.label.replace(/biolink:/g, ''))"
          :subtitle="formatNumber(item.count, true)"
          design="small"
        >
          <AppFlex v-if="item.icon2" gap="tiny" class="association">
            <AppIcon :icon="item.icon" />
            <svg viewBox="0 0 9 2" class="line">
              <line x1="0" y1="1" x2="9" y2="1" />
            </svg>
            <AppIcon :icon="item.icon2" />
          </AppFlex>
        </AppTile>
      </AppGallery>
    </div>
  </AppSection>

  <!-- KG's Tools and Resources -->
  <AppSection width="big">
    <AppHeading class="fullWidthHeader">
      Key Features of the Monarch Knowledge Graph
    </AppHeading>
    <AppGallery :cols="2" class="tools">
      <AppTileCard
        title="Accessible Data and APIs"
        content="Monarch KG offers robust APIs and downloadable datasets, including ontologies, designed for easy integration into external research projects and tools."
        icon="database"
      />
      <AppTileCard
        title="Standards-Based Integration"
        content="Monarch KG follows the Biolink Model to ensure consistent and semantically rich connections across diverse biomedical data sources."
        icon="sitemap"
      />
      <AppTileCard
        title="Regular Updates"
        content="The knowledge graph is updated on a monthly basis to incorporate the latest data and improvements."
        icon="clock-rotate-left"
      />
      <AppTileCard
        title="Cross-Species Insight"
        content="Monarch KG integrates data across multiple species, enabling powerful comparative analyses and translational research."
        icon="microscope"
      />
    </AppGallery>
  </AppSection>

  <!-- Data Harmonization section -->
  <AppSection width="big" class="section">
    <AppHeading class="fullWidthHeader">
      Data Harmonization within the Monarch KG
    </AppHeading>
    <p class="note" style="margin: 1em">
      The descriptions (A–F) correspond to regions marked in the figure below.
    </p>
    <div class="data-harmonization">
      <div class="description-grid">
        <section
          v-for="(point, index) in points"
          :key="index"
          class="figure-point"
        >
          <h3>
            <span class="label">{{ point.label }}</span>
            {{ point.title }}
          </h3>
          <p>{{ point.description }}</p>
        </section>
      </div>
      <figure>
        <img
          src="@/assets/architecture.png"
          alt="Diagram of Monarch infrastructure, described below."
        />
      </figure>
    </div>
    <p class="note">
      Note: This is a partial view of ontologies used. See
      <a
        class="link"
        href="https://github.com/monarch-initiative/phenio/"
        target="_blank"
      >
        PHENIO documentation</a
      >
      for the full list.
    </p>
    <p class="note">
      Follow the progress of the Monarch Initiative and explore related projects
      on
      <a
        class="link"
        href="https://github.com/monarch-initiative"
        target="_blank"
        >GitHub</a
      >.
    </p>
  </AppSection>

  <!-- Contact -->
  <AppSection width="big">
    <p class="info">
      If you have any questions, feel free to reach out to us at :
      <AppLink to="mailto:info@monarchinitiative.org">
        info@monarchinitiative.org
      </AppLink>
    </p>
  </AppSection>
</template>

<script setup lang="ts">
import { startCase } from "lodash";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppSection from "@/components/AppSection.vue";
import AppTileCard from "@/components/AppTileCard.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import metadata from "@/pages/explore/metadata.json";
import { formatNumber } from "@/util/string";

const points = [
  {
    label: "A",
    title: "Entities",
    description:
      "The Monarch KG integrates genes, diseases, and phenotypes using data from diverse biomedical sources.",
  },
  {
    label: "B",
    title: "Data Sources",
    description:
      "External sources like Panther and HPOA feed into the graph through an ingest pipeline.",
  },
  {
    label: "C",
    title: "Ontologies",
    description:
      "Integrated ontologies contribute to a semantic layer conforming to Biolink and PHENIO.",
  },
  {
    label: "D",
    title: "Semantic Unification",
    description:
      "Includes GO (Gene Ontology), BP, MF, CC for harmonizing classification schemas.",
  },
  {
    label: "E",
    title: "Inference",
    description:
      "Enables cross-species reasoning through gene orthology, anatomical homology, and phenotype similarity.",
  },
  {
    label: "F",
    title: "Distribution",
    description:
      "Data is made available via Monarch API, UI, and tools like Exomiser.",
  },
];
</script>

<style lang="scss" scoped>
$wrap: 1000px;

.section.big {
  padding-bottom: unset;
}

.section.center {
  gap: 1em;

  @media (max-width: $wrap) {
    gap: 1.5em;
  }
}

.fullWidthHeader {
  width: 100%;
  padding: 0.6em 0.5em;
  background-color: #d3e6eb;
  color: black;
  text-align: left;
}

.content-container {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 3em;

  @media (max-width: 1100px) {
    flex-direction: column;
    gap: 2em;
  }
}

.text-column,
.video {
  flex: 1 1 48%;
  max-width: 100%;
}

.video {
  aspect-ratio: 16 / 9;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  @media (max-width: 1100px) {
    max-width: 600px;
  }

  iframe {
    display: block;
    width: 100%;
    height: 100%;
    border: none;
  }
}

.enity-association {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 2em;
  gap: 3em;
  background-color: #a6ecf257;
  h1 {
    font-size: 1.4em;
  }
}

.ORIP-video {
  aspect-ratio: 16 / 9;
  width: 65%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);

  @media (max-width: $wrap) {
    width: 100%;
    min-width: 380px;
    max-width: 80%;
  }
}

.association {
  font-size: 2rem;
}

h1 {
  padding: 0;
}

.line {
  width: 10px;

  line {
    stroke: currentColor;
    stroke-width: 2;
    stroke-dasharray: 1 3;
    stroke-linecap: round;
  }
}

.tools {
  margin-top: 0.5em;
  gap: 25px !important;
  @media (max-width: $wrap) {
    margin-top: unset;
  }
}

.info {
  padding: 1em;
}

.kg-about {
  @media (max-width: $wrap) {
    padding-top: 0.7em;
  }
}

.link {
  border-bottom: 1px solid transparent;
  color: #007bff;
  font-weight: 500;
  text-decoration: none;
  transition:
    color 0.3s ease,
    border-bottom 0.3s ease;

  &:hover {
    border-bottom: 1px solid #007bff;
    color: #014791;
  }
}

.tagline {
  position: relative;
  max-width: 800px;
  margin: 1rem auto 0 auto;
  padding: 0 1rem;

  font-weight: 500;
  font-size: 1.1rem;
  text-align: center;

  @media (max-width: $wrap) {
    margin: 0;
  }
}

.data-harmonization {
  display: flex;
  flex-direction: column;

  gap: 1em;

  .description-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5em;

    @media (max-width: $wrap) {
      grid-template-columns: 1fr;
    }
  }

  .figure-point {
    h3 {
      display: flex;
      align-items: center;
      margin-bottom: 0.1em;
      padding: 0;
      gap: 0.5em;

      .label {
        display: inline-block;
        width: 1.6em;
        height: 1.6em;
        border-radius: 50%;
        background-color: #007c91;
        color: white;
        font-size: 0.9rem;
        line-height: 1.6em;
        text-align: center;
      }
    }

    p {
      margin: 0;
      font-size: 0.95rem;
      line-height: 1.5;
    }
  }

  figure {
    align-self: center;
    width: 100%;
    max-width: 850px;
    margin: 1em 4em;
    @media (max-width: 768px) {
      margin: unset;
    }
    img {
      width: 100%;
      height: auto;
    }
  }
}
.note {
  color: #3b3b3b;
  font-size: 0.95rem;
}
p {
  padding-top: 0;
  text-align: left;
}
</style>
