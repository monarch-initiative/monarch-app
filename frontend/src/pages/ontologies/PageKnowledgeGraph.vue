<template>
  <AppBreadcrumb />
  <nav class="navbar">
    <ul>
      <li><a href="#about">About</a></li>
      <li><a href="#contact">Contact</a></li>
      <li><a href="#graph">Image</a></li>
      <li><a href="#cite">Cite</a></li>
    </ul>
  </nav>
  <PageTile id="knowledge-graph" title="Knowledge Graph" />
  <AppSection width="big">
    <p class="tagline">
      Bridging the gap between data and discovery by providing powerful,
      cutting-edge bioinformatics tools that drive innovation and accelerate
      breakthroughs in research.
    </p>
  </AppSection>
  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> About </AppHeading>
    <p>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
      tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
      veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
      commodo consequat. Lorem ipsum dolor sit amet, consectetur adipiscing
      elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
      aliquip ex ea commodo consequat.
    </p>
  </AppSection>
  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> Visual Info </AppHeading>
    <!-- Graph Section -->
    <figure>
      <img
        src="@/assets/architecture.png"
        alt="Diagram of Monarch infrastructure, described below."
      />
    </figure>
  </AppSection>
  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> Resources & Downloads </AppHeading>
    <ul class="links">
      <li>
        <a href="https://github.com/exomiser">https://github.com/exomiser</a>
      </li>
      <li>
        <a href="https://github.com/uberon">https://github.com/uberon</a>
      </li>
    </ul>
  </AppSection>
  <AppSection width="big">
    <AppHeading class="fullWidthHeader">Citation</AppHeading>
    <p>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
      tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
      veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
      commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
      velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
      cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
      est laborum.
    </p>
  </AppSection>
  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> Contact </AppHeading>

    <section id="contact">
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
        commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
        velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
        occaecat cupidatat non proident, sunt in culpa qui officia deserunt
        mollit anim id est laborum.
      </p>
    </section>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTile from "@/components/ThePageTitle.vue";
</script>

<style scoped lang="scss">
.section.big {
  padding-bottom: unset;
}
.section.center {
  gap: 0.7em;
}
.page-layout {
  max-width: 800px;
  margin: auto;
  padding: 2em;
  font-family: sans-serif;
}

.navbar {
  ul {
    display: flex;
    justify-content: center;
    margin-bottom: 2em;
    padding: 0;
    gap: 2em;
    list-style: none;
  }

  li {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 6em;
    height: 1.5em;
    padding: 0;
    background: $gray;
  }

  a {
    color: $white;

    text-align: center;
    text-decoration: none;
  }
}

.tagline {
  width: 70%;
  font-size: 1.1em;
  text-align: center;
}

.fullWidthHeader {
  width: 100%;
  padding: 0.4em 0.5em;
  background-color: #d3e6eb;
  color: black;
  text-align: left;
}

h2 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-size: 1.4rem;
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
.links {
  li {
    margin-bottom: 0.5em;
  }
}
.section:last-of-type {
  margin-bottom: 3em;
}
</style>
