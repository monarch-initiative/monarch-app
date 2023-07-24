<!--
  checkbox with arbitrary content (slot) and icon
-->

<template>
  <aside v-if="open" class="banner">
    <div>
      This web app is a <strong>WORK IN PROGRESS</strong> successor to the
      <a href="https://monarchinitiative.org/">old web app here</a>, and is
      still using
      <strong>
        <a href="https://api.monarchinitiative.org/api/"
          >old data and APIs</a
        ></strong
      >
      that will be replaced soon.
    </div>
    <AppButton icon="times" text="Close" design="small" @click="open = false" />
  </aside>
</template>

<script setup lang="ts">
import { ref } from "vue";

const open = ref(true);
</script>

<style lang="scss" scoped>
.banner {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 20px;
  background: $theme-light;
  text-align: center;
}
</style>
