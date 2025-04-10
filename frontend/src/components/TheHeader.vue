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
          Accelerating precision medicine through Open Data Science
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
      <div v-if="home" class="home">
        <AppLink v-tooltip="'Go to the homepage'" class="logo" to="/">
          <TheLogo class="image" />
          <div class="name">Monarch Initiative</div>
        </AppLink>
      </div>

      <TabSearch
        v-if="search"
        :minimal="true"
        :header-box="true"
        :home="home"
        :class="[home]"
      />

      <!-- <AppLink
        v-tooltip="'Dive right in and use Monarch'"
        class="link"
        to="/explore"
      >
        Explore
      </AppLink> -->
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
              <AppLink
                v-tooltip="subItem.tooltip"
                :to="subItem.to"
                class="linkItems"
              >
                {{ subItem.label }}
                <!-- Conditionally render icon if it's an absolute link -->
                <span v-if="subItem.icon" class="icon">
                  <AppIcon icon="arrow-up-right-from-square" />
                </span>
              </AppLink>
            </li>
          </template>
        </DropdownButton>
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
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import TheLogo from "@/assets/TheLogo.vue";
import navigationMenus from "@/data/navigationMenu.json";
import TabSearch from "@/pages/explore/TabSearch.vue";
import DropdownButton from "./TheDropdownButton.vue";
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
    !(
      route.hash === "#search" ||
      (route.name === "Explore" && route.hash === "") ||
      (route.name === "KnowledgeGraph" && route.hash === "")
    ),
);

/** close nav */
function close() {
  expanded.value = false;
}

/** close nav when page changes */
watch(() => route.name, close);
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
    //commenting this out makes the header not sticky
    //position: relative;
    min-height: 200px;
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
  .link:hover {
    color: hsl(185, 75%, 80%);
  }

  .dropdown :hover {
    color: hsl(185, 75%, 80%); /* Change color on hover */
  }
  @media (max-width: $wrap) {
    flex-direction: column;
    align-items: unset;
    margin-right: auto;
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
  padding: 10px;
  @media (max-width: $wrap) {
    padding: 6.5px;
  }
}
.dropdown-menu li {
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
</style>
