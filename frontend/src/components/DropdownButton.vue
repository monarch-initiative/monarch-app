<template>
  <div class="dropdown">
    <!-- Dropdown button -->
    <button
      @click="$emit('toggle')"
      class="dropdown-btn"
      ref="dropdown"
      @focusout="closeMenu"
      :aria-expanded="isOpen"
    >
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
import { ref, type PropType } from "vue";

// Accept props from the parent
defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  closeMenu: {
    type: Function as PropType<(payload: FocusEvent) => void>,
    required: true,
  },
  handleClickOutside: {
    type: Function,
    required: true,
  },
});

// Dropdown element reference
const dropdown = ref<HTMLElement | null>(null);
</script>

<style lang="scss" scoped>
$wrap: 1000px;

/* Dropdown container */
.dropdown {
  display: inline-block;
  position: relative;
}

/* Dropdown button */
.dropdown-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: transparent;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

.dropdown-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Dropdown arrow */
.dropdown-arrow {
  margin-left: 8px;
  color: white;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.dropdown-btn[aria-expanded="true"] .dropdown-arrow {
  transform: rotate(180deg);
}

/* Dropdown menu (regular size) */
.dropdown-menu {
  z-index: 1000;
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 200px;
  padding: 10px 0;
  overflow: hidden;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

/* Dropdown menu items */
.dropdown-menu ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.dropdown-menu li {
  padding: 12px 16px;
  background-color: #ffffff;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.dropdown-menu li:hover {
  background-color: #f1f1f1;
}

/* Dropdown menu for small screens */
@media (max-width: $wrap) {
  .dropdown-menu {
    position: static;
    width: 100%;
    max-height: 300px; /* Adjust as needed */
    padding: 0;
    overflow-y: auto;
    border: none;
    background-color: #f9f9f9;
    box-shadow: none;
  }
}
</style>
