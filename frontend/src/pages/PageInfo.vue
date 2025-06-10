<template>
  <div class="page-container">
    <AppBreadcrumb :dynamic-breadcrumb="item?.title" />
    <PageTile
      id="page-{{ item?.id || 'not-found' }}"
      :key="`page-${item?.id}`"
      :title="item?.title"
      :img-src="item.icon"
      :is-info-page="true"
      :tagline="item?.tagline"
    />
    <!-- Tabs -->
    <div class="main-content">
      <div class="tabs">
        <button
          v-for="tab in visibleTabs"
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <AppSection
          v-if="activeTab === 'about' && item.description"
          width="big"
        >
          <p>{{ item.description }}</p>
          <div v-if="item.visual_explainer" class="visual-explainer">
            <figure v-if="visualExplainerType === 'image'" class="figure">
              <img :src="item.visual_explainer" alt="Visual explanation." />
            </figure>
            <iframe
              v-else-if="visualExplainerType === 'youtube'"
              :src="embedYouTubeUrl(item.visual_explainer)"
              frameborder="0"
              class="video"
              allow="autoplay; picture-in-picture"
              allowfullscreen
              :title="`Visual explainer video for ${item.title}`"
            ></iframe>
          </div>
        </AppSection>

        <AppSection
          v-if="activeTab === 'citation' && item.Citation"
          width="big"
        >
          <div class="citation-container">
            <p v-html="formattedCitation"></p>
          </div>
        </AppSection>

        <AppSection
          v-if="activeTab === 'resources' && resourceLinks.length"
          width="big"
        >
          <AppLink
            v-for="link in resourceLinks"
            :key="link.key"
            :to="link.value"
            :no-icon="true"
          >
            {{ link.value }}
          </AppLink>
        </AppSection>
      </div>

      <!-- Contact & License (Always Visible) -->
      <AppSection width="big">
        <div class="contact-section">
          <!-- <AppHeading class="header">Contact Us</AppHeading> -->
          <p>
            Have any questions or require assistance? Our support team is happy
            to help.
            <AppLink to="/about/contact-us" class="contact-link"
              >Contact us</AppLink
            >
            today.
          </p>
          <p v-if="item.license && item.license.startsWith('http')">
            This project is licensed. View the full license
            <AppLink
              :to="item.license"
              target="_blank"
              class="license-link"
              :no-icon="true"
              >here</AppLink
            >.
          </p>
          <p v-if="item.license && !item.license.startsWith('http')">
            Content licensed under:
            <span class="license-badge">{{ item.license }}</span>
          </p>
        </div>
      </AppSection>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppLink from "@/components/AppLink.vue";
import AppSection from "@/components/AppSection.vue";
import PageTile from "@/components/ThePageTitle.vue";
import data from "@/data/info-pages.json";

const props = defineProps<{
  itemType: "ontology" | "registry" | "tool";
  id: string;
}>();
const router = useRouter();
const isScrolled = ref(false);
const activeTab = ref("about");

const tabs = [
  { key: "about", label: "About" },
  { key: "citation", label: "Citation" },
  { key: "resources", label: "Resources" },
];

const items = data[props.itemType] as Array<any> | undefined;
const item = computed(() => items?.find((entry) => entry.id === props.id));

const visibleTabs = computed(() => {
  return tabs.filter((tab) => {
    return (
      (tab.key === "about" && item.value?.description) ||
      (tab.key === "citation" && item.value?.Citation) ||
      (tab.key === "resources" && resourceLinks.value.length)
    );
  });
});

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

const resourceLinks = computed(() => {
  const links = [
    { key: "repository", value: item.value?.repository },
    { key: "documentation", value: item.value?.documentation },
    { key: "website", value: item.value?.website },
    { key: "other_link", value: item.value?.other_link },
  ];
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
  return citation.replace(doiRegex, (match: string) => {
    return `<a href="${match}" target="_blank" class="doi-link">${match}</a>`;
  });
});

const visualExplainerType = computed(() => {
  if (!item.value?.visual_explainer) return null;
  return item.value.visual_explainer.includes("youtube.com") ||
    item.value.visual_explainer.includes("youtu.be")
    ? "youtube"
    : "image";
});

const embedYouTubeUrl = (url: string) => {
  const videoIdMatch = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/,
  );
  if (videoIdMatch && videoIdMatch[1]) {
    return `https://www.youtube.com/embed/${videoIdMatch[1]}`;
  }
  return url;
};

watch(item, (newItem) => {
  if (newItem?.title) {
    router.currentRoute.value.meta.breadcrumb = newItem.title;
  }
});
</script>

<style scoped lang="scss">
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 70vh;
  gap: 2.5em;
}

.main-content {
  flex: 1;
}

.section {
  &.big {
    padding: 20px max(20px, (100% - 1200px) / 2) 50px
      max(20px, (100% - 1200px) / 2);
  }
  &.center {
    gap: 15px;
  }
}
.tabs {
  display: flex;
  justify-content: center;

  gap: 1rem;

  button {
    padding: 0.5rem 1.2rem;
    border: none;
    border-radius: 20px;
    background: #f9f9f9;
    color: #333;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
    &:hover {
      background: #e0e0e0;
    }
    &.active {
      background: $theme;
      color: white;
    }
  }
}

.tab-content {
  margin: 2.5em auto 0 auto;
}

.header {
  margin-bottom: 0.8rem;
  font-weight: 600;
  font-size: 1.5rem;
}

.citation-container {
  font-size: 0.95em;
  line-height: 1.6;
  word-wrap: break-word;
  padding: 1rem;
  border-radius: 4px;
  background-color: #f9f9f9;
  a.doi-link {
    color: #005580;
    text-decoration: underline;
    &:hover {
      color: #0077a6;
    }
  }
}

.license-badge {
  display: inline-block;
  padding: 0.3em 0.8em;
  border-radius: 20px;
  background-color: #d3e6eb;
  color: #555;
  font-size: 0.9em;
}

.figure {
  max-width: 100%;
  margin: 1rem auto 2rem;
  text-align: center;
}

.visual-explainer {
  width: 70%;
  padding: 2em;

  .video {
    aspect-ratio: 16 / 9;
    width: 100%;
  }
}
.contact-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}
</style>
