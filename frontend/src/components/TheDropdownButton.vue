<template>
  <div ref="dropdown" class="dropdown" :class="{ 'is-open': isOpen }">
    <button ref="button" class="dropdown-btn" @click="toggleMenu">
      <slot name="button"></slot>
      <span class="dropdown-arrow" :class="{ 'is-rotated': isOpen }"
        >&#9662;</span
      >
    </button>
    <div
      v-if="isOpen"
      ref="menu"
      class="dropdown-menu"
      role="button"
      tabindex="0"
      @click="closeMenu"
      @keydown.enter="closeMenu"
    >
      <ul class="menu-list">
        <slot></slot>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const button = ref<HTMLElement | null>(null);
const menu = ref<HTMLElement | null>(null);

const isOpen = ref(false);
const dropdown = ref<HTMLElement | null>(null);

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const closeMenu = () => {
  isOpen.value = false;
};

const handleClickOutside = (event: MouseEvent) => {
  if (dropdown.value && !dropdown.value.contains(event.target as Node)) {
    closeMenu();
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style lang="scss" scoped>
$wrap: 1350px;

.dropdown {
  display: inline-block;
  position: relative;
  width: max-content;
}

.dropdown-btn {
  display: flex;
  gap: 0.1em;
  font-size: 0.9em;
  white-space: nowrap;
  :hover {
    color: hsl(185, 75%, 80%);
  }
}
li {
  padding-left: 0;
}
.dropdown-menu {
  z-index: 1011;
  position: absolute;
  top: calc(100% + 4px);
  right: 10%;
  width: max-content;
  transform-origin: top;
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
  padding: 0.5rem 1.5em;
  font-size: 1em;
}

/* Show menu when isOpen is true */
.is-open .dropdown-menu {
  transform: scaleY(1);
  opacity: 1;
}

.dropdown-menu::before {
  position: absolute;
  top: -10px;
  right: 8px;
  transform: none;
  border-right: 10px solid transparent;
  border-bottom: 10px solid white;
  border-left: 10px solid transparent;
  content: "";
  filter: drop-shadow(0px -2px 2px rgba(0, 0, 0, 0.1));
}

/* Rotate arrow when dropdown is open */
.dropdown-arrow {
  transition: transform 0.3s ease;
}

.dropdown-arrow.is-rotated {
  transform: rotate(180deg);
}

@media (max-width: $wrap) {
  .dropdown-menu {
    visibility: visible;
    position: relative;
    top: 0.3em;
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
