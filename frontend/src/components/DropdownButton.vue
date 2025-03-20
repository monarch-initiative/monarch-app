<template>
  <div class="dropdown" ref="dropdown" :class="{ 'is-open': isOpen }">
    <button @click="toggleMenu" class="dropdown-btn">
      <slot name="button"></slot>
      <span class="dropdown-arrow">&#9662;</span>
    </button>

    <!-- Dropdown menu -->
    <div v-if="isOpen" class="dropdown-menu">
      <ul class="menu-list">
        <slot></slot>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const isOpen = ref(false);

const toggleMenu = (): void => {
  isOpen.value = !isOpen.value;
};

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (dropdown.value && !dropdown.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
};

const dropdown = ref<HTMLElement | null>(null);

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style lang="scss" scoped>
$wrap: 1000px;

.dropdown {
  display: inline-block;
  position: relative;
}

.dropdown-btn {
  display: flex;
  gap: 0.2em;
}
/* Dropdown menu (hidden by default) */
.dropdown-menu {
  visibility: hidden;
  position: absolute;
  top: calc(100% + 8px);
  min-width: 9em;
  transform: translateY(10px);
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  opacity: 0;
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.menu-list {
  padding: 0.5rem 1em;
}

/* Show menu when isOpen is true */
.is-open .dropdown-menu {
  visibility: visible;
  transform: translateY(0);
  opacity: 1;
}

/* Arrow pointing to button */
.is-open .dropdown-menu::before {
  position: absolute;
  top: -10px;
  left: 20px;
  border-right: 10px solid transparent;
  border-bottom: 10px solid white;
  border-left: 10px solid transparent;
  content: "";
  filter: drop-shadow(0px -2px 2px rgba(0, 0, 0, 0.1));
}

@media (max-width: $wrap) {
  .dropdown-menu {
    visibility: visible;
    position: relative;
    top: 0;
    width: 100%;
    transform: none;
    border: none;
    box-shadow: none;
    opacity: 1;
  }

  .dropdown-menu::before {
    display: none;
  }
}
</style>
