<template>
  <AppBreadcrumb />
  <nav :class="['navbar', { shadow: isScrolled }]">
    <ul>
      <li><a href="#about">About</a></li>
      <li><a href="#resources">Resources</a></li>
      <li><a href="#cite">Cite</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
  </nav>

  <PageTile
    id="page-mondo"
    title="Mondo"
    :img-src="MondoLogo"
    :is-info-page="true"
  />

  <p class="tagline">
    Bridging the gap between data and discovery by providing powerful,
    cutting-edge bioinformatics tools that drive innovation and accelerate
    breakthroughs in research.
  </p>

  <AppSection id="about" width="big">
    <div class="row">
      <div class="column left">
        <AppHeading class="header"> About </AppHeading>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat. Lorem ipsum dolor sit amet,
          consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut
          labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
          exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat.
        </p>
      </div>
      <div class="column right">
        <figure>
          <img
            src="@/assets/architecture.png"
            alt="Diagram of Monarch infrastructure, described below."
          />
        </figure>
      </div>
    </div>
  </AppSection>

  <AppSection id="cite" width="big">
    <div class="row">
      <div class="column left">
        <AppHeading class="header"> Citation </AppHeading>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat.consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat.
        </p>
      </div>
      <div class="column right resource">
        <AppHeading class="header"> Resources & Downloads </AppHeading>
        <ul class="links">
          <li>
            <a href="https://github.com/exomiser"
              >https://github.com/exomiser</a
            >
          </li>
          <li>
            <a href="https://github.com/uberon">https://github.com/uberon</a>
          </li>
        </ul>
      </div>
    </div>
  </AppSection>

  <AppSection id="contact" width="big">
    <p class="contact-text">
      Need more information or support? Don't hesitate to
      <AppLink to="/about/contact-us">Contact Us</AppLink> – we're happy to
      assist you.
    </p>
  </AppSection>

  <AppSection id="license" width="big">
    <p class="license-text">
      The resources and tools provided on this site are released under an open
      license to encourage reuse and collaboration. Click
      <AppLink
        to="https://exomiser.monarchinitiative.org/exomiser/legal"
        target="_blank"
      >
        here
      </AppLink>
      to see full liscence information
    </p>
  </AppSection>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import MondoLogo from "@/assets/icons/resource-mondo-black.svg?url";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTile from "@/components/ThePageTitle.vue";

const isScrolled = ref(false);

const handleScroll = () => {
  isScrolled.value = window.scrollY > 10;
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<style scoped lang="scss">
.section.big {
  padding: 0 max(20px, (100% - 1200px) / 2) 10px;
}

.tagline {
  width: 60%;
  margin: 1.2em auto;
  color: #444;
  font-size: 1.1em;
  text-align: center;
}

.navbar {
  z-index: 999;
  position: sticky;
  top: 78px;
  padding: 1rem 0;
  background-color: #fff;
  transition: box-shadow 0.3s ease;

  .navbar.shadow {
    box-shadow: 0 4px 6px -2px rgba(0, 0, 0, 0.1);
  }

  ul {
    display: flex;
    justify-content: center;
    gap: 2em;
    list-style: none;
  }

  li {
    padding: 0.4em 0.8em;
    border-radius: 4px;
    font-size: 1.1rem;
    transition: background 0.3s ease;
    &:hover {
      background: #e2f0f5;
    }
  }

  a {
    color: #1d1d1d;
    font-weight: 500;
    text-decoration: none;
  }
}

.row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin: 1rem 0;
  gap: 3rem;

  .column {
    flex: 1;
    &.left {
      max-width: 50%;
    }
    &.right {
      max-width: 50%;
      margin-top: 2em;

      figure {
        margin: 0;

        img {
          display: block;
          width: 100%;
          height: auto;
        }
      }
    }
    &.resource {
      margin: 0;
    }
  }
}

.header {
  width: 100%;
  margin-bottom: 1rem;
  color: #1c1c1c;
  font-weight: 700;
  font-size: 1.4rem;
  text-align: left;
}

.links {
  padding: 0;
  list-style: none;

  li {
    margin-bottom: 0.5em;

    a {
      color: #005580;
      text-decoration: underline;
    }
  }
}

#contact,
#license {
  text-align: center;
  .header {
    text-align: center;
  }

  p {
    margin: 0.5em 0;
    color: #333;
  }

  a {
    color: #005580;
    font-weight: 500;
    text-decoration: underline;
    &:hover {
      color: #0077a6;
    }
  }
}

.section:last-of-type {
  margin-bottom: 4em;
}
</style>
