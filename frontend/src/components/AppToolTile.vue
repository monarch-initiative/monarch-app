<template>
  <AppLink :to="to" class="tool-tile">
    <div class="icon-shape">
      <AppIcon v-if="icon" class="icon" :icon="icon" />
    </div>
    <div class="title">{{ title }}</div>
  </AppLink>
</template>

<script setup lang="ts">
interface Props {
  icon?: string;
  to: string;
  title?: string;
}

defineProps<Props>();
</script>

<style scoped lang="scss">
.tool-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.icon-shape {
  display: flex;
  position: relative;
  align-items: center;
  justify-content: center;
  width: 7em;
  height: 7em;
  overflow: visible;
  border-radius: 50%;
  background: radial-gradient(circle at center, #e0f7fa 0%, #afeaf4 80%);
  @media (max-width: 1100px) {
    width: 5em;
    height: 5em;
  }
}

.icon {
  z-index: 2;
  position: relative;
  width: 4em;
  height: 4em;

  @media (max-width: 1100px) {
    width: 3em;
    height: 3em;
  }
}

.title {
  color: inherit;
  font-size: 1rem;
  text-align: center;
}
</style>
