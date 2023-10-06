import domtoimage from "dom-to-image";
import { stringify } from "@/util/object";

/** download blob as file */
export const download = (
  data: BlobPart,
  filename: string | string[],
  type: string,
  ext: string,
) => {
  const blob = new Blob([data], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download =
    [filename]
      .flat()
      .join("_")
      .replaceAll(/[^ A-Za-z0-9_-]/g, " ")
      .replaceAll(/\s+/g, "-") +
    "." +
    ext;
  link.click();
  window.URL.revokeObjectURL(url);
};

/** download blob as png */
export const downloadPng = (data: BlobPart, filename: string | string[]) =>
  download(data, filename, "image/png", "png");

/** download data as json file */
export const downloadJson = (data = {}, filename: string | string[]) =>
  download(stringify(data, 2), filename, "application/json", "json");

/** get screenshot blob from dom element */
export const getScreenshot = async (
  element: HTMLElement,
  scale = window.devicePixelRatio,
) => {
  /** actual client size */
  let { width = 1000, height = 1000 } = element.getBoundingClientRect() || {};

  /** upscale for better quality */
  if (scale !== 1) {
    width *= scale;
    height *= scale;
  }

  /** alternatives: rasterizeHTML.js, html2canvas */
  return await domtoimage.toBlob(element || document, {
    width,
    height,
    /** match transform origin with element alignment */
    style: scale !== 1 && {
      transform: `scale(${scale})`,
      transformOrigin: "center",
    },
  });
};
