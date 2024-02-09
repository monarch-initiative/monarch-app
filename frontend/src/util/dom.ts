import { sleep } from "@/util/debug";

/** safely get document object */
export const safeDocument = () =>
  typeof document === "undefined" ? undefined : document;

/** restart an element's CSS animations programmatically */
export const restartAnimations = (element: Element): void => {
  if (element instanceof Element)
    for (const animation of element.getAnimations()) {
      animation.cancel();
      animation.play();
    }
};

/** wait for element matching selector to appear, checking periodically */
export const waitFor = async <El extends Element>(
  selector: string,
): Promise<El | undefined> => {
  const waits = [
    0, 1, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000,
  ];
  while (waits.length) {
    const match = safeDocument()?.querySelector<El>(selector);
    if (match) return match;
    await sleep(waits.shift());
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
export const screenToSvgCoords = (svg: SVGSVGElement, x: number, y: number) => {
  /**
   * https://bugzilla.mozilla.org/show_bug.cgi?id=543965 no viable workarounds
   * found
   */
  if (!svg.getCTM()) return;
  let point = svg.createSVGPoint();
  point.x = x;
  point.y = y;
  point = point.matrixTransform(svg.getCTM()?.inverse());
  return point;
};

const canvas = document.createElement("canvas");
const ctx = canvas?.getContext("2d");

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
