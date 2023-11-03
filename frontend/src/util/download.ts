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

/** download element as svg file */
export const downloadSvg = (
  element: SVGSVGElement,
  filename: string,
  removeAttrs: RegExp[] = [/class/, /^data-/, /^aria-/, /tabindex/, /role/],
) => {
  const clone = element.cloneNode(true) as SVGSVGElement;
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  for (const element of clone.querySelectorAll("*"))
    for (const removeAttr of removeAttrs)
      for (const { name } of [...element.attributes])
        if (name.match(removeAttr)) element.removeAttribute(name);
  const data = clone.outerHTML;
  download(data, filename, "image/svg+xml", "svg");
};

/** download data as json file */
export const downloadJson = (data = {}, filename: string | string[]) =>
  download(stringify(data, 2), filename, "application/json", "json");
