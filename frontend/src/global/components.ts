import AppButton from "@/components/AppButton.vue";
import AppFlex from "@/components/AppFlex.vue";
import AppGallery from "@/components/AppGallery.vue";
import AppHeading from "@/components/AppHeading.vue";
import AppIcon from "@/components/AppIcon.vue";
import AppLink from "@/components/AppLink.vue";
import AppMarkdown from "@/components/AppMarkdown.vue";
import AppPlaceholder from "@/components/AppPlaceholder.vue";
import AppSection from "@/components/AppSection.vue";
import AppStatus from "@/components/AppStatus.vue";
import AppTile from "@/components/AppTile.vue";

/**
 * list of components we want to be available in any vue file without importing.
 * only include components used very repetitively.
 */
const globalComponents = {
  AppButton,
  AppFlex,
  AppGallery,
  AppHeading,
  AppIcon,
  AppLink,
  AppMarkdown,
  AppPlaceholder,
  AppSection,
  AppStatus,
  AppTile,
};

export default globalComponents;
