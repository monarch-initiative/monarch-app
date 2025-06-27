<template>
  <AppSection v-if="item?.about" width="big">
    <div class="formatted-about" v-html="formattedAbout"></div>
    <p>
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
import { computed } from 'vue';
import AppLink from "@/components/AppLink.vue";
import AppSection from "@/components/AppSection.vue";
import { embedYouTubeUrl } from "../helpers/youtube";

const props = defineProps<{
  item: Record<string, any>;
  externalLink: { href: string; text: string } | null;
  explainerParts: {
    videoUrl?: string;
    imageId?: string;
    description?: string;
  };
}>();
console.log('about',props.item.about)

const formattedAbout = computed(() => {
  const text = props.item.about ?? "";

  const blocks = text.split(/\n{2,}|\n/).filter(Boolean);

  const formatted = blocks.map((block: string) => {
    // If block has multiple inline dashes and one or more " - "
    const dashSegments = block.split(/\s-\s/);

    if (dashSegments.length > 2) {
      const intro = dashSegments[0].trim();
      const bullets = dashSegments.slice(1);

      const listItems: string[] = [];
      let trailingParagraph = "";

      bullets.forEach((b, index) => {
        const trimmed = b.trim();

        // If last bullet has a period and trailing sentence, split it out
        if (index === bullets.length - 1) {
          const periodIdx = trimmed.indexOf(". ");
          if (periodIdx > -1 && periodIdx < trimmed.length - 1) {
            listItems.push(`<li>${trimmed.slice(0, periodIdx + 1)}</li>`);
            trailingParagraph = trimmed.slice(periodIdx + 1).trim();
          } else {
            listItems.push(`<li>${trimmed}</li>`);
          }
        } else {
          listItems.push(`<li>${trimmed}</li>`);
        }
      });

      return `<p>${intro}</p><ul>${listItems.join("")}</ul>${
        trailingParagraph ? `<p>${trailingParagraph}</p>` : ""
      }`;
    }

    return `<p>${block.trim()}</p>`;
  });

  return formatted.join("");
});



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
// .formatted-about ::v-deep p {
//   margin-bottom: 1em;
// }

.formatted-about ul {
  margin-bottom: 1em;
  padding-left: 1.25em; /* optional: indent list */
}

.formatted-about li {
  margin-bottom: 0.25em; /* optional: space between list items */
}


</style>
