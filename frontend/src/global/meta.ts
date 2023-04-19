import { ref, watch } from "vue";

/**
 * index.html is statically generated with hard-coded meta data, from
 * environment variables specified in the .env file. convert these values into
 * reactive variables so we can change them and update the document tags during
 * run time
 */

/** multi-part page title. array. gets joined with a | separator. */
export const appTitle = ref([import.meta.env.VITE_TITLE]);
/** page meta description */
export const appDescription = ref(import.meta.env.VITE_DESCRIPTION);
/** page canonical url meta */
export const appUrl = ref(import.meta.env.VITE_DESCRIPTION);

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

/** set meta data value */
const setTag = (property = "", value = "") =>
  document
    .querySelector(`meta[name='${property}'], meta[property='${property}']`)
    ?.setAttribute("content", value);
