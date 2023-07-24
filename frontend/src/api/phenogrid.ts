import "phenogrid/dist/phenogrid-bundle.js";
import "./phenogrid.css";
import { sleep } from "@/util/debug";
import { waitFor } from "@/util/dom";
import { biolink } from "./";

/** mount phenogrid to dom element with options */
export const mountPhenogrid = async (
  selector: string,
  xAxis: { id?: string; name?: string }[],
  yAxis: { id?: string; name?: string }[],
  mode = "compare"
): Promise<void> => {
  /**
   * wait for phenogrid container to render on mount, and clear any previous
   * phenogrid instances from showing
   */
  const container = await waitFor("#phenogrid");
  if (container) container.innerHTML = "";

  /** map in particular way based on mode, per ui 2.0 */
  const modifiedXAxis = xAxis.map(({ id = "", name = "" }) =>
    mode === "compare" ? [id] : { groupId: id, groupName: name }
  );

  Phenogrid.createPhenogridForElement(document?.querySelector(selector), {
    serverURL: biolink + "/",
    forceBiolink: true,
    appURL: window.location.origin,
    gridSkeletonData: {
      title: " ",
      xAxis: modifiedXAxis,
      yAxis: yAxis.map(({ id = "", name = "" }) => ({ id, term: name })),
    },
    selectedCalculation: 0,
    selectedSort: "Frequency",
    geneList: modifiedXAxis,
    owlSimFunction: mode,
  });

  /** wait for phenogrid to load */
  const svg = await waitFor<SVGSVGElement>("#phenogrid_svg");

  /** fit a few times after, while phenogrid renders elements */
  patchSvg(svg);
  for (let repeat = 0; repeat < 5; repeat++) {
    await sleep(500);
    patchSvg(svg);
  }
};

/** fix incorrect svg sizing */
const patchSvg = (svg: SVGSVGElement | undefined, padding = 20) => {
  if (!svg) return;

  const { x, y, width, height } = svg.getBBox();
  /** set view box to bbox, essentially fitting view to content */
  const viewBox = [
    x - padding,
    y - padding,
    width + padding * 2,
    height + padding * 2,
  ]
    .map((v) => Math.round(v))
    .join(" ");

  svg.setAttribute("viewBox", viewBox);
  svg.removeAttribute("width");
  svg.removeAttribute("height");
};

declare global {
  const Phenogrid: PhenogridType;
}

/** typescript definition for phenogrid */
type PhenogridType = {
  createPhenogridForElement: (
    element: HTMLElement | null,
    options: {
      serverURL: string;
      forceBiolink: boolean;
      appURL: string;
      gridSkeletonData: {
        title: string;
        xAxis: ({ groupId: string; groupName: string } | string[])[];
        yAxis: { id: string; term: string }[];
      };
      selectedCalculation: number;
      selectedSort: string;
      geneList: ({ groupId: string; groupName: string } | string[])[];
      owlSimFunction: string;
    }
  ) => void;
};
