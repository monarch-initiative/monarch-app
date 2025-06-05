<template>
  <AppBreadcrumb />
  <nav :class="['navbar', { shadow: isScrolled }]">
    <ul>
      <li v-if="item.description"><a href="#about">About</a></li>
      <li v-if="resourceLinks.length"><a href="#resources">Resources</a></li>
      <li v-if="item.Citation"><a href="#cite">Cite</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
  </nav>

  <PageTile
    id="page-{{ item?.id || 'not-found' }}"
    :title="item?.title"
    :img-src="MondoLogo"
    :is-info-page="true"
    :tagline="item?.tagline"
  />

  <AppSection id="about" width="big">
    <AppHeading class="header">About</AppHeading>
    <p>{{ item.description }}</p>
    <figure v-if="item.visual_explainer" class="figure">
      <img
        :src="`/assets/${item.visual_explainer}`"
        alt="Visual explanation."
      />
    </figure>
  </AppSection>

  <!-- Citation & Resources Section -->
  <AppSection id="cite" width="big" v-if="item.Citation">
    <AppHeading class="header">Citation</AppHeading>
    <div class="citation-container">
      <p v-html="formattedCitation"></p>
    </div>
  </AppSection>

  <AppSection width="big" v-if="resourceLinks.length">
    <AppHeading class="header" id="resources">Resources & Downloads</AppHeading>

    <AppLink
      v-for="link in resourceLinks"
      :key="link.key"
      :to="link.value"
      :noIcon="true"
    >
      {{ link.value }}
    </AppLink>
  </AppSection>

  <!-- Contact Section -->
  <AppSection id="contact" width="big">
    <div class="contact-section">
      <AppHeading class="header">Contact Us</AppHeading>
      <p>
        Have any questions or require assistance? Our support team is happy to
        help.
        <AppLink to="/about/contact-us" class="contact-link">
          Contact us
        </AppLink>
        today.
      </p>
    </div>
  </AppSection>

  <!-- License Section -->
  <AppSection id="license" width="big" v-if="item.license">
    <div class="license-section">
      <AppHeading class="header">License</AppHeading>
      <p v-if="item.license.startsWith('http')">
        This project is licensed.View the full license
        <AppLink
          :to="item.license"
          target="_blank"
          class="license-link"
          :noIcon="true"
        >
          here </AppLink
        >.
      </p>
      <p v-else>
        Content licensed under:
        <span class="license-badge">{{ item.license }}</span>
      </p>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import MondoLogo from "@/assets/icons/resource-mondo-black.svg?url";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppLink from "@/components/AppLink.vue";
import AppSection from "@/components/AppSection.vue";
import PageTile from "@/components/ThePageTitle.vue";
import data from "@/data/info-pages.json";

const props = defineProps<{
  itemType: "ontology" | "registry" | "standard" | "tool";
  id: string;
}>();

const isScrolled = ref(false);

const items = data[props.itemType] as Array<any> | undefined;
const item = computed(() => items?.find((entry) => entry.id === props.id));

const handleScroll = () => {
  isScrolled.value = window.scrollY > 10;
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", handleScroll);
});

if (!item.value) {
  console.warn(`No item found for type=${props.itemType} and id=${props.id}`);
}

//resource links
const resourceLinks = computed(() => {
  const links = [
    { key: "repository", value: item.value?.repository },
    { key: "documentation", value: item.value?.documentation },
    { key: "website", value: item.value?.website },
    { key: "other_link", value: item.value?.other_link },
  ];

  // Remove empty values and duplicate URLs
  const seen = new Set<string>();
  const uniqueLinks = [];

  for (const link of links) {
    if (link.value && !seen.has(link.value)) {
      seen.add(link.value);
      uniqueLinks.push(link);
    }
  }
  return uniqueLinks;
});

const formattedCitation = computed(() => {
  if (!item.value?.Citation) return "";
  const citation = item.value.Citation;
  const doiRegex = /(https?:\/\/[^\s]+)/g;
  const citationWithLink = citation.replace(doiRegex, (match: string) => {
    return `<a href="${match}" target="_blank" class="doi-link">${match}</a>`;
  });
  return citationWithLink;
});
</script>

<style scoped lang="scss">
.section {
  &.big {
    align-items: unset;
    padding: 0 max(20px, (100% - 1200px) / 2) 10px;
    text-align: left;
  }

  &.center {
    gap: 10px;
  }
  a {
    color: #005580;
    text-decoration: none;
    &:hover {
      color: #0077a6;
    }
  }

  figure {
    max-width: 50em;
    margin: 1rem auto;
    img {
      display: block;
      width: 100%;
      height: auto;
    }
  }
}
.section:last-of-type {
  margin-bottom: 2em;
}
:deep([id]) {
  scroll-margin-top: 180px;
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

  &.shadow {
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
  }

  &.single-column {
    flex-direction: column;
    align-items: flex-start; // align children left
    justify-content: flex-start;

    .column {
      max-width: 100%;
      text-align: left;
    }

    .column.right {
      display: none;
    }
  }
}

.header {
  width: 100%;
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

      &:hover {
        color: #0077a6;
      }
    }
  }
}

.citation-container {
  font-size: 0.95em;
  line-height: 1.6;
  word-wrap: break-word;
  padding: 1rem;

  border-radius: 4px;
  background-color: #f9f9f9;
  white-space: pre-line;
  overflow-wrap: break-word;

  a.doi-link {
    color: #005580;
    font-weight: 500;
    text-decoration: underline;

    &:hover {
      color: #0077a6;
    }
  }
}

#contact,
#license {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  border-radius: 8px;
  background-color: #f9f9f9; // soft background

  .header {
    margin-bottom: 0.5rem;
  }

  p {
    color: #444;
    font-size: 0.95rem;
    line-height: 1.6;
  }

  a {
    color: #0077a6;
    font-weight: 500;
    text-decoration: underline;

    &:hover {
      color: #005580;
    }
  }
}
</style>
