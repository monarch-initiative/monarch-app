<template>
  <div class="page-container">
    <AppBreadcrumb :dynamic-breadcrumb="item?.title" />
    <PageTile
      :id="item?.title_short?.toLowerCase() ?? 'not-found'"
      :key="`page-${item?.title_short}`"
      :title="item?.title"
      :img-src="item?.icon || ''"
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
        <AppSection v-if="activeTab === 'about' && item?.about" width="big">
          <p>{{ item.about }}</p>
          <div v-if="item.visual_explainer" class="visual-explainer">
            <div
              class="video"
              v-if="
                explainerParts.videoUrl &&
                /youtu\.?be/.test(explainerParts.videoUrl)
              "
            >
              <h2>Watch: What Is {{ item?.title }} and Why It Matters</h2>
              <!-- YouTube video -->
              <iframe
                :src="embedYouTubeUrl(explainerParts.videoUrl)"
                frameborder="0"
                allow="autoplay; picture-in-picture"
                allowfullscreen
                :title="`Visual explainer video for ${item.title}`"
              ></iframe>
            </div>

            <!-- Description Text -->
            <p v-if="explainerParts.description">
              {{ explainerParts.description }}
            </p>

            <!-- Image -->
            <figure v-if="explainerParts.imageId">
              <img
                :src="`/icons/${explainerParts.imageId}.png`"
                :alt="`Visual explainer image for ${item.title}`"
              />
            </figure>
          </div>
        </AppSection>

        <AppSection
          v-if="activeTab === 'citation' && item.citation"
          width="big"
        >
          <div class="citation-container">
            <pre ref="citationText" class="citation-box"
              >{{ item.citation }}
    </pre
            >

            <AppButton
              text="Copy Citation"
              @click="copyCitation"
              class="copy-btn"
            />
            <span v-if="copied" class="copied-msg">Copied!</span>
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
import { useRoute, useRouter } from "vue-router";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppLink from "@/components/AppLink.vue";
import AppSection from "@/components/AppSection.vue";
import PageTile from "@/components/ThePageTitle.vue";
import rawData from "@/resources/monarch-app-infopages.json";

/* ------------------------------------------------------------------ */
/* 1. Type helpers – keep them minimal so we don’t over-specify       */
/* ------------------------------------------------------------------ */
type CategoryKey = "ontologies" | "registries" | "standards" | "tools";
type ItemRecord = Record<string, any>; // one item (ecto / hp / etc.)
type DataShape = Record<CategoryKey, ItemRecord>; // whole JSON file

const data = rawData as DataShape; // cast once, use everywhere

/* ------------------------------------------------------------------ */
/* 2. Props from router / parent                                      */
/* ------------------------------------------------------------------ */
const props = defineProps<{
  itemType: CategoryKey;
  id: string;
}>();

/* ------------------------------------------------------------------ */
/* 3. Reactive state                                                 */
/* ------------------------------------------------------------------ */
const router = useRouter();
const route = useRoute();
const isScrolled = ref(false);
const activeTab = ref<"about" | "citation" | "resources">("about");

/* ------------------------------------------------------------------ */
/* 4. Lookup the single item directly (object pattern)                */
/* ------------------------------------------------------------------ */

const item = computed(() => {
  const isStandardAliasedAsTool =
    props.itemType === "tools" && ["phenopackets", "sssom"].includes(props.id);

  // Pull from standards if aliased, otherwise normal lookup
  if (isStandardAliasedAsTool) {
    return data.standards?.[props.id] ?? null;
  }

  return data[props.itemType]?.[props.id] ?? null;
});

/* ------------------------------------------------------------------ */
/* 5. Tabs logic                                                      */
/* ------------------------------------------------------------------ */
const tabs = [
  { key: "about", label: "About" },
  { key: "citation", label: "Citation" },
  { key: "resources", label: "Resources" },
];

const resourceLinks = computed(() => {
  const sel = item.value?.see_also ?? {};
  const links = [
    { key: "repository", value: sel.repository },
    { key: "documentation", value: sel.documentation },
    { key: "website", value: sel.website },
    { key: "other", value: sel.other },
  ];
  const seen = new Set<string>();
  return links.filter(
    (l) => l.value && !seen.has(l.value) && seen.add(l.value),
  );
});

const visibleTabs = computed(() =>
  tabs.filter(
    (t) =>
      (t.key === "about" && item.value?.about) ||
      (t.key === "citation" && item.value?.citation) ||
      (t.key === "resources" && resourceLinks.value.length),
  ),
);

/* ------------------------------------------------------------------ */
/* 6. Helpers – citation formatting & media type detection            */
/* ------------------------------------------------------------------ */
// const formattedCitation = computed(() => {
//   const text = item.value?.Citation ?? "";
//   return text.replace(
//     /(https?:\/\/[^\s]+)/g,
//     (m) => `<a href="${m}" target="_blank" class="doi-link">${m}</a>`,
//   );
// });

// const visualExplainerType = computed<"youtube" | "image" | null>(() => {
//   const v = item.value?.visual_explainer;
//   if (!v) return null;
//   return /youtu\.?be/.test(v) ? "youtube" : "image";
// });

const embedYouTubeUrl = (url: string) => {
  const videoIdMatch = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/,
  );
  if (videoIdMatch && videoIdMatch[1]) {
    return `https://www.youtube.com/embed/${videoIdMatch[1]}`;
  }
  return url; // fallback: just return original
};

const explainerParts = computed(() => {
  const raw = item.value?.visual_explainer;
  if (!raw) return {};

  const parts = raw
    .split("|||")
    .map((s) => s.trim())
    .filter(Boolean);

  let videoUrl: string | undefined;
  let imageId: string | undefined;
  let description = "";

  for (const p of parts) {
    if (/youtu\.?be|youtube\.com/.test(p)) {
      // video?
      videoUrl = p;
    } else if (p.startsWith("figure-")) {
      // image reference?
      imageId = p; // keep the id (no extension)
    } else {
      // anything else is text
      description = p;
    }
  }

  return { videoUrl, imageId, description };
});

/* ------------------------------------------------------------------ */
/* Scroll / breadcrumb effects                                     */
/* ------------------------------------------------------------------ */
const handleScroll = () => (isScrolled.value = window.scrollY > 10);
onMounted(() => window.addEventListener("scroll", handleScroll));
onBeforeUnmount(() => window.removeEventListener("scroll", handleScroll));

/* ------------------------------------------------------------------ */
/*  Copy Citation                        */
/* ------------------------------------------------------------------ */
const copied = ref(false);
const citationText = ref<HTMLElement | null>(null);

function copyCitation() {
  if (citationText.value) {
    const text = citationText.value.innerText;
    navigator.clipboard.writeText(text).then(() => {
      copied.value = true;
      setTimeout(() => (copied.value = false), 2000);
    });
  }
}

watch(item, (newItem) => {
  if (newItem?.title) router.currentRoute.value.meta.breadcrumb = newItem.title;
});

watch(
  () => route.params.id,
  () => {
    // force recomputation of `item`
    item.value = data[route.params.itemType]?.[route.params.id];
  },
);

if (!item.value)
  console.warn(`No item found for ${props.itemType}/${props.id}`);
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

.visual-explainer {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin: 1.2em auto;
  gap: 2rem;
  h2 {
    text-align: left;
  }
  .video {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 1.5rem;
    iframe {
      aspect-ratio: 16 / 9;
      width: 70%;
      border-radius: 8px;
    }
  }
  img {
    align-self: center;
    width: 70%;
  }
}

.contact-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.citation-box {
  padding: 1rem;
  border-radius: 8px;
  background: #f7f7f7;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

.copy-btn {
  margin-top: 0.5rem;
  padding: 0.4rem 1rem;
  border: none;
  border-radius: 5px;
  background-color: $theme-light;
  color: black;

  cursor: pointer;
}

.copy-btn:hover {
  background-color: #005580;
}

.copied-msg {
  display: inline-block;
  margin-left: 1rem;
  color: green;
  font-size: 0.9rem;
}
</style>
