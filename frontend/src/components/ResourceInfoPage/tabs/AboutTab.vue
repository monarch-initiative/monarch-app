<template>
  <AppSection v-if="item?.about" width="big">
    <p>
      {{ item.about }}
      <template v-if="externalLink">
        Learn more about
        <AppLink :to="externalLink.href" :no-icon="true" class="external-link">
          {{ externalLink.text }}.
        </AppLink>
      </template>
    </p>

    <div v-if="item.visual_explainer" class="visual-explainer">
      <div
        class="video"
        v-if="
          explainerParts.videoUrl && /youtu\.?be/.test(explainerParts.videoUrl)
        "
      >
        <h2>Watch: What Is {{ item?.title }} and Why It Matters</h2>
        <iframe
          :src="embedYouTubeUrl(explainerParts.videoUrl)"
          frameborder="0"
          allow="autoplay; picture-in-picture"
          allowfullscreen
          :title="`Visual explainer video for ${item.title}`"
        ></iframe>
      </div>

      <p v-if="explainerParts.description">{{ explainerParts.description }}</p>

      <figure v-if="explainerParts.imageId">
        <img
          :src="`/icons/${explainerParts.imageId}.png`"
          :alt="`Visual explainer image for ${item.title}`"
        />
      </figure>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import AppLink from "@/components/AppLink.vue";
import AppSection from "@/components/AppSection.vue";
import { embedYouTubeUrl } from "../helpers/youtube";

defineProps<{
  item: Record<string, any>;
  externalLink: { href: string; text: string } | null;
  explainerParts: {
    videoUrl?: string;
    imageId?: string;
    description?: string;
  };
}>();
</script>

<style scoped lang="scss">
$wrap: 1000px;

.external-link {
  text-decoration: none;
}

.visual-explainer {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin: 1.2em auto;
  gap: 2rem;
  h2 {
    text-align: left;
  }
  .video {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 1.5rem;
    iframe {
      aspect-ratio: 16 / 9;
      width: 70%;
      border-radius: 8px;

      @media (max-width: $wrap) {
        width: 100%;
      }
    }
  }
  img {
    align-self: center;
    width: 70%;
  }
}
</style>
