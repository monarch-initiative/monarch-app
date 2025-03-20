<template>
  <div class="dropdown" ref="dropdown">
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

// Reactive state to track if the dropdown is open
const isOpen = ref(false);

// Toggle the dropdown visibility
const toggleMenu = (): void => {
  isOpen.value = !isOpen.value;
};

// Close the dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (dropdown.value && !dropdown.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
};

// Dropdown element reference
const dropdown = ref<HTMLElement | null>(null);

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style lang="scss" scoped>
$wrap: 1000px; /* Define the breakpoints using $wrap */

/* Dropdown container */
.dropdown {
  display: inline-block;
  position: relative;
}

/* Dropdown menu (regular size) */
.dropdown-menu {
  z-index: 1000;
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 10em;
  overflow: hidden;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.dropdown-menu ul {
  display: block;
  margin: 0;
  padding: 0.5em;
  font-size: 0.8em;
  white-space: nowrap;
}

/* Dropdown menu for small screens */
@media (max-width: $wrap) {
  .dropdown-menu {
    position: relative;
    width: 100%;
    max-height: 300px; /* Adjust as needed */
    padding: 0;
    overflow-y: auto;
    border: none;
    background-color: #f9f9f9;
    box-shadow: none;
  }

  .dropdown-arrow {
    margin-left: 8px;
    color: white;
    font-size: 12px;
    transition: transform 0.3s ease;
  }
}
</style>
