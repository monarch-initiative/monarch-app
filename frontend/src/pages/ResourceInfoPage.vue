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
        <AboutTab
          v-if="activeTab === 'about' && item?.about"
          :item="item"
          :external-link="externalLink"
          :explainer-parts="explainerParts"
        />
        <CitationTab
          v-if="activeTab === 'citation' && item?.citation"
          :item="item"
        />
        <ResourcesTab
          v-if="activeTab === 'resources' && item?.see_also"
          :item="item"
        />
      </div>

      <AppSection width="big">
        <div class="contact-section">
          <p class="inline-contact">
            Contact:
            <span v-if="item.contact?.name">{{ item.contact.name }}</span>
            <span v-if="item.contact?.email">
              |
              <a :href="`mailto:${item.contact.email}`">{{
                item.contact.email
              }}</a></span
            >
            <span v-if="item.contact?.github">
              | GitHub:
              <a
                :href="`https://github.com/${item.contact.github.replace('@', '')}`"
                target="_blank"
                >{{ item.contact.github }}</a
              ></span
            >
            <span v-if="item.contact?.orcid">
              | ORCID:
              <a :href="item.contact.orcid" target="_blank">{{
                item.contact.orcid.replace("https://", "")
              }}</a></span
            >
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
import { computed, nextTick, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import AboutTab from "@/components/ResourceInfoPage/tabs/AboutTab.vue";
import CitationTab from "@/components/ResourceInfoPage/tabs/CitationTab.vue";
import ResourcesTab from "@/components/ResourceInfoPage/tabs/ResourcesTab.vue";
import PageTile from "@/components/ThePageTitle.vue";
import { ABOUT_PAGE_LINKS } from "@/data/aboutPageLinks";
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
const tabs: { key: "about" | "citation" | "resources"; label: string }[] = [
  { key: "about", label: "About" },
  { key: "citation", label: "Citation" },
  { key: "resources", label: "Resources" },
];

const externalLink = computed(() => {
  console.log("item", item.value);
  const title = item?.value?.title;
  return ABOUT_PAGE_LINKS[title || ""];
});

const resourceLinks = computed(() => {
  const raw = item.value?.see_also ?? {};
  const seen = new Set<string>();
  const links: { key: string; value: string }[] = [];

  const add = (key: string, url: string) => {
    if (url && !seen.has(url)) {
      links.push({ key, value: url });
      seen.add(url);
    }
  };

  add("website", raw.website);

  Object.keys(raw)
    .filter((k) => k !== "website" && k !== "other")
    .sort()
    .forEach((k) => {
      const urls = Array.isArray(raw[k]) ? raw[k] : [raw[k]];
      urls.forEach((url) => typeof url === "string" && add(k, url.trim()));
    });

  const other = raw.other;
  (Array.isArray(other) ? other : [other]).forEach(
    (url) => typeof url === "string" && add("other", url.trim()),
  );

  return links;
});

const visibleTabs = computed(() =>
  tabs.filter(
    (t) =>
      (t.key === "about" && item.value?.about) ||
      (t.key === "citation" && item.value?.citation) ||
      (t.key === "resources" && resourceLinks.value.length),
  ),
);

const embedYouTubeUrl = (url: string) => {
  const videoIdMatch = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/,
  );
  if (videoIdMatch && videoIdMatch[1]) {
    return `https://www.youtube.com/embed/${videoIdMatch[1]}`;
  }
  return url;
};

const explainerParts = computed(() => {
  const raw = item.value?.visual_explainer;
  if (!raw) return {};

  const parts = raw
    .split("|||")
    .map((s: string) => s.trim())
    .filter(Boolean);

  let videoUrl: string | undefined;
  let imageId: string | undefined;
  let description = "";

  for (const p of parts) {
    if (/youtu\.?be|youtube\.com/.test(p)) {
      videoUrl = p;
    } else if (p.startsWith("figure-")) {
      imageId = p;
    } else {
      description = p;
    }
  }

  return { videoUrl, imageId, description };
});

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

function formatApaCitation(rawCitation: string): string {
  const trimmed = rawCitation.trim();

  // Case 1: "Cite the GH repo" type
  if (/^Cite the GH repo/i.test(trimmed)) {
    const url = trimmed.split(":")[1]?.trim();
    const project =
      url?.split("/").pop()?.replace(/-/g, " ") || "GitHub Project";
    return `${capitalizeWords(project)}. (n.d.). Retrieved from ${url}`;
  }

  // Case 2: Bare URL
  if (/^https?:\/\//.test(trimmed)) {
    const url = new URL(trimmed);
    return `${url.hostname.replace("www.", "")}. (n.d.). Retrieved from ${trimmed}`;
  }

  // Case 3: Contains DOI/PMID/PMCID or journal-looking content
  if (/doi|PMID|PMCID|[A-Z][a-z]+ J[a-z]*\./.test(trimmed)) {
    const sentenceEnded = trimmed.endsWith(".") ? trimmed : trimmed + ".";
    return sentenceEnded;
  }

  return `(n.d.). ${trimmed}`;
}

function capitalizeWords(str: string): string {
  return str.replace(/\b\w/g, (char) => char.toUpperCase());
}

watch(
  () => [route.fullPath, item.value?.title],
  async () => {
    await nextTick(); // wait for DOM and reactivity to settle

    if (item.value?.title) {
      document.title = item.value.title;
      router.currentRoute.value.meta.breadcrumb = item.value.title;
    } else {
      document.title = "Monarch Initiative";
    }

    activeTab.value = "about";
  },
  { immediate: true },
);

if (!item.value)
  console.warn(`No item found for ${props.itemType}/${props.id}`);
</script>

<style scoped lang="scss">
$wrap: 1000px;
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

.license-badge {
  display: inline-block;
  padding: 0.3em 0.8em;
  border-radius: 20px;
  background-color: #d3e6eb;
  color: #555;
  font-size: 0.9em;
}

.contact-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.inline-contact a {
  text-decoration: none;
}

.inline-contact a:hover {
  text-decoration: underline;
}

.external-link {
  text-decoration: none;
}
</style>
