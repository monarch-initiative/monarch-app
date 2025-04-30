<template>
  <div class="tile">
    <div class="left-icon">
      <AppIcon v-if="icon" :icon="icon" :size="'1.5em'" class="icon" />
    </div>
    <div class="tile-body">
      <h3 class="title">{{ title }}</h3>
      <p class="tile-content">{{ content }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  content: string;
  buttonText?: string;
  icon?: string;
}>();
</script>

<style lang="scss" scoped>
$wrap: 1100px;

.tile {
  display: flex;
  align-items: flex-start;
  max-width: 600px;
  padding: 1.5rem 1rem;
  gap: 0.8rem;
  border: 1px solid #d5f1f8;
  border-radius: 12px;
  background-color: #e6fbff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  @media (max-width: $wrap) {
    flex-direction: column;
    align-items: left;
    gap: 1em;
    text-align: center;
  }
}

.left-icon {
  display: flex;
  flex-shrink: 0;
  align-items: flex-start;
  justify-content: center;

  .icon {
    color: #007a99;
  }
}

.tile-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.8rem;
}

.title {
  margin: 0;
  font-weight: 600;
  font-size: 1.25rem;
  text-align: left;
}
h3 {
  padding: 0;
}
.tile-content {
  color: #333;
  font-size: 1rem;
}
</style>
