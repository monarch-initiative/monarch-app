import { sleep } from "@/util/debug";

/** restart an element's CSS animations programmatically */
export const restartAnimations = (element: Element): void => {
  if (element instanceof Element)
    for (const animation of element.getAnimations()) {
      animation.cancel();
      animation.play();
    }
};

/**
 * wait for element matching selector to appear. check several times per sec,
 * with hard limit. when found, return found element and run callback with
 * element
 */
export const waitFor = async <El extends Element>(
  selector = "",
  timeout = 3000,
  interval = 50,
): Promise<El | undefined> => {
  for (let check = 0; check < timeout / interval; check++) {
    const match = document?.querySelector<El>(selector);
    if (match) return match;
    await sleep(interval);
  }
};

/** find index of first element "in view". model behavior off of wikiwand.com. */
export const firstInView = (elements: HTMLElement[]): number => {
  const offset = document.querySelector("header")?.clientHeight || 0;
  for (let index = elements.length - 1; index >= 0; index--)
    if (elements[index].getBoundingClientRect().top < offset + 100)
      return index;
  return 0;
};
