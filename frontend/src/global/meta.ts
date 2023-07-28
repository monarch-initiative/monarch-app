import { ref, watch } from "vue";

/**
 * index.html is hard-coded with metadata from the .env file. to change/update
 * the document metadata tags at runtime, change one of these reactive
 * variables.
 */

/** multi-part page title as array, gets joined with a | separator */
export const appTitle = ref<string[]>([import.meta.env.VITE_TITLE]);
/** page meta description */
export const appDescription = ref<string>(import.meta.env.VITE_DESCRIPTION);
/** page canonical url meta */
export const appUrl = ref<string>(import.meta.env.VITE_DESCRIPTION);

/** update document title meta tags */
watch(appTitle, () => {
  const title = appTitle.value
    .concat([import.meta.env.VITE_TITLE])
    .filter((part) => part)
    .join(" | ");

  document.title = title || "";
  setTag("title", title);
  setTag("og:title", title);
  setTag("twitter:title", title);
});

/** update document description meta tags */
watch(appDescription, () => {
  setTag("description", appDescription.value);
  setTag("og:description", appDescription.value);
  setTag("twitter:description", appDescription.value);
});

/** update document url meta tags */
watch(appUrl, () => {
  document
    .querySelector("link[rel='canonical']")
    ?.setAttribute("href", appUrl.value || "");
  setTag("og:url", appUrl.value);
  setTag("twitter:url", appUrl.value);
});

/** set metadata value */
const setTag = (property = "", value = "") =>
  document
    .querySelector(`meta[name='${property}'], meta[property='${property}']`)
    ?.setAttribute("content", value);
