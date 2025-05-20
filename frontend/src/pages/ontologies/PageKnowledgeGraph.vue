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
  <div class="page-title">
    <PageTile
      id="knowledge-graph"
      title="Knowledge Graph"
      imageSrc="/icons/monarch-logo.svg"
    />
  </div>

  <p class="tagline">
    Bridging the gap between data and discovery by providing powerful,
    cutting-edge bioinformatics tools that drive innovation and accelerate
    breakthroughs in research.
  </p>

  <AppSection width="big">
    <div class="card">
      <AppHeading class="fullWidthHeader"> About </AppHeading>
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
        commodo consequat. Lorem ipsum dolor sit amet, consectetur adipiscing
        elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
        ut aliquip ex ea commodo consequat.
      </p>
    </div>
  </AppSection>

  <AppSection width="big">
    <div class="card">
      <AppHeading class="fullWidthHeader"> Visual Info </AppHeading>
      <figure>
        <img
          src="@/assets/architecture.png"
          alt="Diagram of Monarch infrastructure, described below."
        />
      </figure>
    </div>
  </AppSection>

  <AppSection width="big">
    <div class="card">
      <AppHeading class="fullWidthHeader"> Resources & Downloads </AppHeading>
      <ul class="links">
        <li>
          <a href="https://github.com/exomiser">https://github.com/exomiser</a>
        </li>
        <li>
          <a href="https://github.com/uberon">https://github.com/uberon</a>
        </li>
      </ul>
    </div>
  </AppSection>

  <AppSection width="big">
    <div class="card">
      <AppHeading class="fullWidthHeader">Citation</AppHeading>
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
        commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
        velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
        occaecat cupidatat non proident, sunt in culpa qui officia deserunt
        mollit anim id est laborum.
      </p>
    </div>
  </AppSection>
  <AppSection width="big">
    <div class="card">
      <AppHeading class="fullWidthHeader"> Contact </AppHeading>

      <section id="contact">
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
          culpa qui officia deserunt mollit anim id est laborum.
        </p>
      </section>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTile from "@/components/ThePageTitle.vue";
</script>

<style scoped lang="scss">
.section {
  p {
    margin-bottom: 1em;
  }
}
.section.center {
  gap: 1em;

  h2 {
    margin: 0;
    padding: 0;
  }
}

.section.big {
  padding: 0 max(20px, (100% - 1200px) / 2);
}
.page-title {
  margin-bottom: 1em;
  text-align: center;

  img {
    max-height: 60px;
    margin-bottom: 0.5em;
  }

  h1 {
    color: #2c3e50;
    font-weight: 600;
    font-size: 1.6rem;
  }
}
.page-title {
  img {
    max-height: 60px;
  }
}
.card {
  width: 100%;
  margin-bottom: 2.5rem;
  padding: 2rem;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background-color: #f7f7f7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition:
    box-shadow 0.3s ease,
    transform 0.3s ease;
}

.navbar {
  margin-bottom: 1em;
  gap: 1.2em;
  ul {
    display: flex;
    justify-content: center;
    margin: 0;
    padding: 0;
    gap: 2em;
    list-style: none;
  }

  li {
    padding: 0.4em 0.8em;
    border-radius: 6px;
    border-radius: 4px;

    background: #e0eef2;
    font-size: 0.9rem;
    transition: background 0.3s ease;
    &:hover {
      background: #b4d3da;
    }
  }

  a {
    color: #1d1d1d;
    font-weight: 500;
    font-size: 0.95em;
    text-decoration: none;
  }
}

.tagline {
  width: 60%;
  margin: 0 auto 2em auto;
  color: #555;
  font-size: 1.1em;
  text-align: center;
}

.fullWidthHeader {
  width: 100%;
  color: #1c1c1c;
  font-weight: 600;
  text-align: left;
}

figure {
  display: flex;
  justify-content: center;
  padding: 0 4em;

  img {
    max-width: 100%;
    height: auto;
  }
}

.links {
  li {
    margin-bottom: 0.5em;

    a {
      color: #005580;
      text-decoration: underline;
    }
  }
}

.section:last-of-type {
  margin-bottom: 4em;
}

h2 {
  margin-bottom: 0.6rem;
  color: #2c3e50;
  font-size: 1.3rem;
}
</style>
