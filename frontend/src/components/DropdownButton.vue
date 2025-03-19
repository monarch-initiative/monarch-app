<template>
  <div class="dropdown">
    <!-- Dropdown button -->
    <button
      @click="$emit('toggle')"
      class="dropdown-btn"
      ref="dropdown"
      @focusout="closeMenu"
    >
      <slot name="button"></slot>
      <span class="dropdown-arrow">&#9662;</span>
      <!-- Unicode arrow -->
    </button>

    <!-- Dropdown menu -->
    <div v-if="isOpen" class="dropdown-menu">
      <slot></slot>
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

const dropdown = ref<HTMLElement | null>(null);
</script>

<style scoped>
/* Dropdown container */
.dropdown {
  display: inline-block;
  position: relative;
}

/* Dropdown button */
.dropdown-btn {
  border: none;
  cursor: pointer;
}

/* Dropdown menu */
.dropdown-menu {
  z-index: 1000;
  position: absolute;
  top: 100%;
  left: 0; /* Align to the right */
  min-width: 100px;
  transform: translateY(0);
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  opacity: 1;
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
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.dropdown-menu li:hover {
  background-color: #f1f1f1;
}

/* Responsive adjustments */
@media (max-width: 1000px) {
  .dropdown-menu {
    right: auto;
    left: 0;
    width: 100%;
  }
}

.dropdown-btn {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  color: white;

  cursor: pointer;
}

.dropdown-arrow {
  margin-left: 8px;
  color: white;
  font-size: 12px;
  transition: transform 0.3s ease; /* Add a smooth rotation effect */
}

.dropdown-btn[aria-expanded="true"] .dropdown-arrow {
  transform: rotate(180deg); /* Rotate the arrow when the dropdown is open */
}
</style>
