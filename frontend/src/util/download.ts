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
  removeEls: string[] = ["clipPath"],
  removeAttrs: RegExp[] = [/class/, /^data-/, /^aria-/, /tabindex/, /role/],
) => {
  /** make editable clone of svg node */
  const clone = element.cloneNode(true) as SVGSVGElement;
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");

  /** cleanup */

  /** remove unneeded elements */
  for (const selector of removeEls)
    for (const element of clone.querySelectorAll(selector)) element.remove();

  /** remove unneeded attributes on every element */
  for (const element of clone.querySelectorAll("*"))
    for (const removeAttr of removeAttrs)
      for (const { name } of [...element.attributes])
        if (name.match(removeAttr)) element.removeAttribute(name);

  /** append to document so bbox not 0's */
  document.body.append(clone);

  /** fit viewbox to contents */
  const { x, y, width, height } = clone.getBBox();
  clone.setAttribute("viewBox", [x, y, width, height].join(" "));

  /** download modified source */
  download(clone.outerHTML, filename, "image/svg+xml", "svg");

  clone.remove();
};

/** download data as json file */
export const downloadJson = (data = {}, filename: string | string[]) =>
  download(stringify(data, 2), filename, "application/json", "json");
