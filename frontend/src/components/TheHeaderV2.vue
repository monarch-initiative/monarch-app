<template>
  <header class="header">
    <div class="nav-wrapper">
      <!-- Top row: logo + hamburger -->
      <div class="branding">
        <AppLink class="logo" to="/">
          <TheLogo class="image" />
          <div class="name">Monarch Initiative</div>
        </AppLink>

        <!-- Mobile menu toggle -->
        <button
          class="menu-toggle"
          @click="expanded = !expanded"
          :aria-expanded="expanded"
        >
          <AppIcon :icon="expanded ? 'xmark' : 'bars'" />
        </button>
      </div>

      <!-- Dropdown nav -->
      <div class="navItems" :class="{ expanded }">
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
                <span v-if="subItem.icon" class="icon">
                  <AppIcon icon="arrow-up-right-from-square" />
                </span>
              </AppLink>
            </li>
          </template>
        </DropdownButton>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import TheLogo from "@/assets/TheLogo.vue";
import navigationMenus from "@/data/navigationMenu.json";
import DropdownButton from "./TheDropdownButton.vue";

const expanded = ref(false);
function handleResize() {
  if (window.innerWidth >= 1000) {
    expanded.value = false;
  }
}

onMounted(() => {
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
});
</script>

<style lang="scss" scoped>
$wrap: 1000px;

.header {
  z-index: 1010;
  padding: 1rem;
  background: $theme;
  color: $white;
}

.nav-wrapper {
  display: flex;
  flex-direction: column;

  @media (min-width: $wrap) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.branding {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.logo {
  display: flex;
  align-items: center;
  color: inherit;
  text-decoration: none;

  .image {
    height: 40px;
    margin-right: 10px;
  }

  .name {
    font-weight: bold;
    text-transform: uppercase;
  }
}

.menu-toggle {
  border: none;
  background: none;
  color: white;
  font-size: 1.5rem;

  @media (min-width: $wrap) {
    display: none;
  }
}

.navItems {
  display: none;

  &.expanded {
    display: flex;
    flex-direction: column;
    margin-top: 1rem;
    gap: 0.5rem;
  }
  .dropdown:hover {
    color: hsl(185, 75%, 80%);
  }

  @media (min-width: $wrap) {
    display: flex !important;
    flex-direction: row;
    margin-top: 0;
    gap: 1rem;
  }
}

.dropdown-button {
  padding: 10px;
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

.icon {
  height: 0.8em;
}
</style>
