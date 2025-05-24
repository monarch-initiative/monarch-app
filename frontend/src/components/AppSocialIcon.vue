<template>
  <span :class="['social-icon', type]">
    <AppLink :to="url">
      <AppIcon :icon="icon" />
    </AppLink>
  </span>
</template>

<script setup lang="ts">
defineProps<{
  type: string;
  icon: string;
  url: string;
}>();
</script>
<style scoped lang="scss">
.social-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #000;
  transition: transform 0.2s ease;

  .app-icon {
    color: white;
    font-size: 1rem;
  }

  &:hover {
    transform: scale(1.1);
  }
}

// Platform-specific colors
.social-icon.email {
  background-color: #007acc;
}

.social-icon.medium {
  background-color: #000000;
}

.social-icon.github {
  background-color: #333333;
}

.social-icon.linkedin {
  background-color: #0a66c2;
}

.social-icon.youtube {
  background-color: #ff0000;
}

.social-icon.bluesky {
  background-color: rgba(48, 184, 230, 0.2);

  .app-icon {
    height: 1.2em;
    margin-top: 0.45em;
  }
}
</style>
