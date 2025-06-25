<!--
  floating header at top of every page
-->

<template>
  <header id="header" ref="header" :class="['header', { home, sticky: !home || isMobile }]">
    <!-- :style="{
      position: !home || isMobile ? 'sticky' : 'static',
    }" -->
    <TheNexus v-if="home" />

    <div class="title">
      <AppLink
        v-tooltip="home ? '' : 'Homepage'"
        :to="home ? '' : '/'"
        :class="['navLogo', { home }]"
      >
        <TheLogo class="image" />
        <component :is="'div'" class="name"> Monarch Initiative </component>
      </AppLink>

      <button
        v-tooltip="expanded ? 'Close navigation menu' : 'Expand navigation menu'"
        class="button"
        :aria-expanded="expanded"
        @click="expanded = !expanded"
      >
        <AppIcon :icon="expanded ? 'xmark' : 'bars'" />
      </button>
    </div>
    <div v-if="!isMobile && home" class="center-section">
      <div v-if="!isMobile && home" class="hero-card">
        <div class="hero-header">
          <TheLogo class="hero-logo" />
          <h1>
            Search Across <br />
            <strong>Genes, Diseases & Phenotypes</strong>
          </h1>
        </div>

        <div class="hero-search-wrapper">
          <TabSearch :minimal="true" :header-box="true" :home="home" />
          <TheSearchTerms />
          <TheSearchSuggestions @select="handleSuggestionClick" />
          <div class="hero-tool-links">
            <h3 class="hero-tools-label">Explore knowledge graph tools:</h3>
            <AppLink to="/phenotype-similarity">Phenotype Search</AppLink>
            <span>|</span>
            <AppLink to="/text-annotator">Text Annotator</AppLink>
          </div>
        </div>
      </div>
    </div>

    <nav :class="['nav', { home, expanded }]">
      <div class="home">
        <AppLink v-if="!isMobile" v-tooltip="'Go to the homepage'" class="logo" to="/">
          <TheLogo class="image" />
          <div class="name">Monarch Initiative</div>
        </AppLink>
      </div>

      <TabSearch
        v-if="search && (isMobile || !home)"
        :minimal="true"
        :header-box="true"
        :home="home"
      />

      <div class="navItems">
        <DropdownButton
          v-for="(menu, index) in navigationMenus"
          :key="menu.label"
          :index="index"
          :label="menu.label"
          class="dropdown-button"
        >
          <template #button>{{ menu.label }}</template>
          <template #default>
            <li v-for="subItem in menu.subItems || []" :key="subItem.label">
              <AppLink v-tooltip="subItem.tooltip" :to="subItem.to" class="linkItems">
                {{ subItem.label }}
                <span v-if="subItem.icon" class="icon">
                  <AppIcon icon="arrow-up-right-from-square" />
                </span>
              </AppLink>
            </li>
          </template>
        </DropdownButton>
      </div>
    </nav>

    <TheScrollButton v-if="!isMobile && home" />
  </header>
</template>

<script setup lang="ts">
  import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import TheLogo from "@/assets/TheLogo.vue";
  import TabSearch from "@/components/TabSearch.vue";
  import TheSearchTerms from "@/components/TheSearchTerms.vue";
  import navigationMenus from "@/data/navigationMenu.json";
  import { ENTITY_MAP } from "@/data/toolEntityConfig";
  import DropdownButton from "./TheDropdownButton.vue";
  import TheNexus from "./TheNexus.vue";
  import TheScrollButton from "./TheScrollButton.vue";
  import TheSearchSuggestions from "./TheSearchSuggestions.vue";

  /** route info */
  const route = useRoute();
  const router = useRouter();
  /** is nav menu expanded */
  const expanded = ref(false);

  /** header element */
  const header = ref<HTMLElement>();

  /** is home page (big) version */
  const home = computed((): boolean => route.name === "Home");

  /** whether to show search box */
  const search = computed(
    (): boolean =>
      !(
        route.hash === "#search" ||
        (route.name === "Explore" && route.hash === "") ||
        (route.name === "KnowledgeGraph" && route.hash === "")
      ),
  );

  function scrollToHashWithOffset(hash: string, offset = 80) {
    const el = document.querySelector(hash);
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  }

  const handleSuggestionClick = async (term: string) => {
    const entity = ENTITY_MAP[term];
    if (entity?.id) {
      await router.push({ path: "/" + entity.id, hash: "#" + entity.to });

      await nextTick();
      setTimeout(() => {
        scrollToHashWithOffset(`#${entity.to}`, 80);
      }, 1000);
    }
  };

  /** close nav */
  function close() {
    expanded.value = false;
  }

  const windowWidth = ref(window.innerWidth);

  const updateWidth = () => {
    windowWidth.value = window.innerWidth;
  };

  onMounted(() => {
    window.addEventListener("resize", updateWidth);
  });

  onUnmounted(() => {
    window.removeEventListener("resize", updateWidth);
  });

  const isMobile = computed(() => windowWidth.value < 1120);

  /** close nav when page changes */
  watch(() => route.name, close);
</script>

<style lang="scss" scoped>
  $wrap: 1120px;

  /** header */
  .header {
    display: flex;
    z-index: 1010;
    position: relative;
    top: 0;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    background: $theme;
    color: $white;
  }
  .sticky {
    position: sticky;
  }
  .navLogo {
    display: flex;
    align-items: center;
    padding: 10px;
    color: $white;
    text-decoration: none;
  }
  @media not all and (max-width: $wrap) {
    .navLogo {
      display: none;
    }
  }

  @media (max-width: $wrap) {
    .header {
      flex-direction: column;
    }

    .header.home {
      justify-content: space-between;
    }
  }

  @media not all and (max-width: $wrap) {
    .header.home {
      min-height: calc(100vh - 64px);
    }
    .header.home .title {
      margin-top: 70px;
      margin-bottom: 20px;
    }
  }

  /** title bar (containing logo and nav toggle button) */

  .title {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .button {
    width: 50px;
    height: 50px;
  }

  @media not all and (max-width: $wrap) {
    .button {
      display: none;
    }
  }

  @media (max-width: $wrap) {
    .title {
      width: 100%;
    }
  }

  .center-section {
    display: flex;
    z-index: 1010;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 0 1rem;
  }
  /** logo image and text */

  .logo {
    display: flex;
    align-items: center;
    padding: 10px;
    color: $white;
    text-decoration: none;
  }

  .image {
    height: 45px;
    padding: 5px;
  }

  .name {
    padding: 5px;
    font-weight: 400;
    font-size: 1.1rem;
    line-height: $spacing - 0.3;
    letter-spacing: 1px;
    text-align: center;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .slogan {
    padding: 5px;
    font-size: 1rem;
  }

  @media (max-width: $wrap) {
    .logo {
      padding: 5px;
    }

    .image {
      height: 40px;
    }

    .name {
      font-size: 1rem;
      text-align: left;
    }

    .slogan {
      display: none;
    }
  }

  @media not all and (max-width: $wrap) {
    .logo.home {
      flex-direction: column;

      .image {
        height: 70px;
      }

      .name {
        width: min-content;
        font-size: 1.1rem;
      }
    }
  }

  /** navigation bar */

  .nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 15px;
    gap: 10px;
  }

  .link {
    position: relative;
    max-width: 100%;
    padding: 10px;
    color: $white;
    text-align: center;
    text-decoration: none;
  }

  @media (max-width: $wrap) {
    .nav {
      position: unset;
      flex-direction: column;
      margin-top: -10px;

      &.expanded {
        transition: max-height 0.3s ease-out;
      }
    }

    .nav:not(.expanded) {
      display: none;
    }

    .link {
      width: 200px;
      padding: 5px;

      @media (max-width: $wrap) {
        text-align: left;
      }
    }
  }

  @media not all and (max-width: $wrap) {
    .nav.home {
      position: absolute;
      top: 0;
      right: 0;
    }
  }

  .navItems {
    display: flex;
    align-items: center;
    padding: 0 1rem;

    .link:hover,
    .dropdown:hover {
      color: hsl(185, 75%, 80%);
    }

    @media (max-width: $wrap) {
      flex-direction: column;
      align-items: unset;
      margin-right: auto;
      padding: unset;
      gap: 0.1em;
    }
  }

  /* Adjust TabSearch component when screen width is less than $wrap */
  @media (max-width: $wrap) {
    .tab-search {
      max-height: 20px;
    }
  }

  /**This is temperory. When we replce the whole navbigation menu with dropdowns,
we can remove this and adjust onw styling to the whole menu items.
Its here to align with the styling of old nav items. */
  .dropdown-button {
    padding: 8px;
    @media (max-width: $wrap) {
      padding: 6.5px;
    }
  }
  .dropdown-menu li {
    padding: 0;
    font-size: 0.8em;
    list-style: none;
  }
  .dropdown-menu li a {
    text-decoration: none !important;
  }
  .linkItems {
    display: flex;
    align-items: flex-start;
    gap: 0.8em;
  }

  .icon {
    height: 0.8em;
  }

  .hero-card {
    display: flex;
    flex-direction: column;
    width: 80%;
    max-width: 68em;
    margin: 0 auto;
    padding: 2.5em 2em;
    gap: 1.2em;
    border-radius: 20px;
    background: white;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    color: #222;
    text-align: center;
    transition: box-shadow 0.3s ease;

    @media (max-width: 1300px) {
      padding: 1.8em;
    }
  }

  .hero-card:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  }
  .hero-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1em;
  }

  .hero-header h1 {
    color: #333;
    font-weight: 600;
    font-size: 1.75em;
    strong {
      display: block;
      font-size: 1.1em;
    }
  }

  .hero-search-wrapper {
    display: flex;
    position: relative;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    gap: 1em;
  }

  .hero-logo {
    height: 50px;
  }
  .hero-tool-links {
    display: flex;
    flex-wrap: nowrap;

    margin-top: 1.8rem;
    gap: 0.75rem;
    font-size: 1.1em;
    white-space: nowrap;
    a {
      color: #007c8a;
      font-weight: 500;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }

    span {
      color: #aaa;
    }
    h3 {
      padding: 0;
    }
  }
  .hero-tools-label {
    color: rgb(90, 95, 95);
    font-weight: 500;
    text-align: center;
  }
</style>
