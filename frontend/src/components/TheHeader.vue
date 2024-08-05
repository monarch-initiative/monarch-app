<!--
  floating header at top of every page
-->

<template>
  <header ref="header" :class="['header', { home }]">
    <!-- header background visualization -->
    <TheNexus v-if="home" />

    <!-- title bar -->
    <div class="title">
      <!-- logo image and text -->
      <AppLink
        v-tooltip="home ? '' : 'Homepage'"
        :to="home ? '' : '/'"
        :class="['logo', { home }]"
      >
        <TheLogo class="image" />
        <!-- make logo text the h1 on homepage -->
        <component :is="home ? 'h1' : 'div'" class="name">
          Monarch Initiative
        </component>
        <!-- slogan -->
        <div v-if="home" class="slogan">
          Accelerating precision medicine through open data science
        </div>
      </AppLink>

      <!-- nav toggle button -->
      <button
        v-tooltip="
          expanded ? 'Close navigation menu' : 'Expand navigation menu'
        "
        class="button"
        :aria-expanded="expanded"
        @click="expanded = !expanded"
      >
        <AppIcon :icon="expanded ? 'xmark' : 'bars'" />
      </button>
    </div>

    <!-- navigation bar -->
    <nav :class="['nav', { home, expanded }]">
      <TabSearch v-if="search" :minimal="true" :header-box="true" />

      <AppLink
        v-tooltip="'Dive right in and use Monarch'"
        class="link"
        to="/explore"
      >
        Explore
      </AppLink>
      <AppLink
        v-tooltip="'Citing, licensing, sources, and other info'"
        class="link"
        to="/about"
      >
        About
      </AppLink>
      <AppLink
        v-tooltip="'Feedback, docs, guides, contact, and more'"
        class="link"
        to="/help"
      >
        Help
      </AppLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { onClickOutside } from "@vueuse/core";
import TheLogo from "@/assets/TheLogo.vue";
import TabSearch from "@/pages/explore/TabSearch.vue";
import TheNexus from "./TheNexus.vue";

/** route info */
const route = useRoute();

/** is nav menu expanded */
const expanded = ref(false);

/** header element */
const header = ref<HTMLElement>();

/** is home page (big) version */
const home = computed((): boolean => route.name === "Home");

/** whether to show search box */
const search = computed(
  (): boolean =>
    route.name !== "Home" &&
    !(
      route.hash === "#search" ||
      (route.name === "Explore" && route.hash === "")
    ),
);

/** close nav */
function close() {
  expanded.value = false;
}

/** close nav when page changes */
watch(() => route.name, close);

/** close nav when clicking outside header */
onClickOutside(header, close);
</script>

<style lang="scss" scoped>
$wrap: 1000px;

/** header */

.header {
  display: flex;
  z-index: 1010;
  position: sticky;
  top: 0;
  align-items: center;
  justify-content: space-between;
  background: $theme;
  color: $white;
}

.header.home {
  justify-content: center;
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
    position: relative;
    min-height: 300px;
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
  justify-content: flex-end;
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

  &:after {
    position: absolute;
    right: 50%;
    bottom: 0;
    left: 50%;
    height: 2px;
    background: $white;
    content: "";
    transition:
      left $fast,
      right $fast;
  }

  &:hover:after {
    right: 5px;
    left: 5px;
  }
}

@media (max-width: $wrap) {
  .nav {
    position: unset;
    flex-direction: column;
    margin-top: -10px;
  }

  .nav:not(.expanded) {
    display: none;
  }

  .link {
    width: 200px;
    padding: 5px;
  }
}

@media not all and (max-width: $wrap) {
  .nav.home {
    position: absolute;
    top: 0;
    right: 0;
  }
}
</style>
