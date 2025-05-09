<template>
  <button class="scroll-button" @click="scrollToHomePageSection">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="32"
      height="32"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="feather feather-chevron-down"
      viewBox="0 0 24 24"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { nextTick } from "vue";

function scrollToHomePageSection() {
  const el = document.getElementById("home-page");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  } else {
    console.warn("home-page not found");
  }
}
</script>

<style scoped>
.scroll-button {
  margin-bottom: 2rem;
  border: none;
  border-radius: 50%;
  background: white;
  color: #555;
  animation: bounce 2s infinite;
  cursor: pointer;
  cursor: pointer;
  filter: drop-shadow(rgba(0, 0, 0, 0.5) 1px 1px 2px);
}
</style>
