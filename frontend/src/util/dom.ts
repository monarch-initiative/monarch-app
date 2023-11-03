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

/** convert screen coordinates to svg coordinates */
export const screenToSvgCoords = (
  svg: SVGSVGElement | undefined,
  x: number,
  y: number,
) => {
  /** https://bugzilla.mozilla.org/show_bug.cgi?id=543965 */
  if (!svg || !svg.getCTM()) return new DOMPoint(0, 0);
  let point = svg.createSVGPoint();
  point.x = x;
  point.y = y;
  point = point.matrixTransform(svg.getCTM()?.inverse());
  return point;
};

const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
/** calculate dimensions of given font */
export const getTextSize = (text: string, font: string) => {
  if (!ctx) return new TextMetrics();
  ctx.font = font;
  return ctx.measureText(text);
};

/** truncate text by displayed size instead of # of characters */
export const truncateBySize = (
  text: string,
  limit: number,
  font: string = "10px Poppins",
) => {
  if (getTextSize(text, font).width < limit) return text;
  while (getTextSize(text + "...", font).width > limit && text.length > 3)
    text = text.slice(0, -1);
  return text + "...";
};
