<!--
  floating header at top of every page
-->

<template>
  <header ref="header" class="header" :data-home="home">
    <!-- header background visualization -->
    <TheNexus v-if="home" />

    <!-- title bar -->
    <div class="title" :title="app.version">
      <!-- logo image and text -->
      <AppLink
        v-tooltip="home ? '' : 'Homepage'"
        :to="home ? '' : '/'"
        class="logo"
        :data-home="home"
      >
        <TheLogo class="image" />
        <!-- make logo text the h1 on homepage -->
        <component :is="home ? 'h1' : 'div'" class="text">
          Monarch Initiative
        </component>
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
        <AppIcon :icon="expanded ? 'times' : 'bars'" />
      </button>
    </div>

    <!-- navigation bar -->
    <nav class="nav" :data-home="home" :data-expanded="expanded">
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
import app from "../../package.json";
import TheNexus from "./TheNexus.vue";

/** route info */
const route = useRoute();

/** is nav menu expanded */
const expanded = ref(false);

/** header element */
const header = ref<HTMLElement>();

/** is home page (big) version */
const home = computed((): boolean => route.name === "Home");

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
$wrap: 600px;

/** header */

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: $theme-dark;
  color: $white;
  z-index: 10;
}

.header[data-home="true"] {
  justify-content: center;
}

@media (max-width: $wrap) {
  .header {
    flex-direction: column;
  }

  .header[data-home="true"] {
    justify-content: space-between;
  }
}

@media not all and (max-width: $wrap) {
  .header[data-home="true"] {
    position: relative;
    min-height: 300px;
  }
}

/** title bar (containing logo and nav toggle button) */

.title {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.text {
  padding: 5px;
  font-size: 1.1rem;
  text-align: center;
  font-weight: 400;
  letter-spacing: 1px;
  line-height: $spacing - 0.3;
  text-transform: uppercase;
  white-space: nowrap;
}

@media (max-width: $wrap) {
  .logo {
    padding: 5px;
  }

  .image {
    height: 40px;
  }

  .text {
    font-size: 1rem;
    text-align: left;
  }
}

@media not all and (max-width: $wrap) {
  .logo[data-home="true"] {
    flex-direction: column;

    .image {
      height: 70px;
    }

    .text {
      font-size: 1.1rem;
      width: min-content;
    }
  }
}

/** navigation bar */

.nav {
  display: flex;
  gap: 10px;
  padding: 15px;
}

.link {
  position: relative;
  padding: 10px;
  color: $white;
  text-decoration: none;
  text-align: center;

  &:after {
    content: "";
    position: absolute;
    left: 50%;
    right: 50%;
    bottom: 0;
    height: 2px;
    background: $white;
    transition: left $fast, right $fast;
  }

  &:hover:after {
    left: 5px;
    right: 5px;
  }
}

@media (max-width: $wrap) {
  .nav {
    flex-wrap: wrap;
    justify-content: center;
    position: unset;
    margin-top: -10px;
  }

  .nav[data-expanded="false"] {
    display: none;
  }

  .link {
    padding: 5px;
  }
}

@media not all and (max-width: $wrap) {
  .nav[data-home="true"] {
    position: absolute;
    top: 0;
    right: 0;
  }
}
</style>
