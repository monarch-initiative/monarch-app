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
          v-for="(menu, index) in menus"
          :key="menu.label"
          :index="index"
          :label="menu.label"
        >
          <template #button>{{ menu.label }}</template>

          <template #default>
            <li v-for="subItem in menu.subItems" :key="subItem.label">
              <a :href="subItem.link">{{ subItem.label }}</a>
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import TheLogo from "@/assets/TheLogo.vue";
import menus from "@/data/menu.json";
import TabSearch from "@/pages/explore/TabSearch.vue";
import DropdownButton from "./DropdownButton.vue";
import TheNexus from "./TheNexus.vue";

/** route info */
const route = useRoute();

/** is nav menu expanded */
const expanded = ref(false);

/** header element */
const header = ref<HTMLElement>();

// Reactive state to track if the dropdown is open
const isOpen = ref(false);

/** is home page (big) version */
const home = computed((): boolean => route.name === "Home");

const openIndex = ref<number | null>(null);

/** whether to show search box */
const search = computed(
  (): boolean =>
    !(
      route.hash === "#search" ||
      (route.name === "Explore" && route.hash === "")
    ),
);

/** close nav */
function close() {
  expanded.value = false;
}

// Toggle the dropdown menu visibility
// const toggleMenu = (index: number) => {
//   openIndex.value = openIndex.value === index ? null : index;
// };

// Close the dropdown menu
const closeMenu = (): void => {
  isOpen.value = false;
};

// // Handle clicks outside the dropdown
// const handleClickOutside = (event: MouseEvent): void => {
//   const dropdown = document.querySelector(".dropdown");
//   if (dropdown && !dropdown.contains(event.target as Node)) {
//     closeMenu();
//   }
// };

// Add and remove event listeners for outside clicks

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
    margin-right: auto;
    padding: 5px 0;
  }
}

/* Adjust TabSearch component when screen width is less than $wrap */
@media (max-width: $wrap) {
  .tab-search {
    max-height: 20px;
  }
}

.dropdown-menu li {
  list-style: none;
}
.dropdown-menu li a {
  text-decoration: none !important;
}
</style>
