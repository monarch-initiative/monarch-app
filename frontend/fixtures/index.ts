import { rest } from "msw";
import { biolink, monarch } from "@/api";
import { feedbackEndpoint } from "@/api/feedback";
import { efetch, esummary } from "@/api/publications";
import { uptimeRobot } from "@/api/uptime";
import associationsTable from "./association-table.json";
import associations from "./associations.json";
import autocomplete from "./autocomplete.json";
import datasets from "./datasets.json";
import feedback from "./feedback.json";
import histopheno from "./histopheno.json";
import nodePublicationAbstract from "./node-publication-abstract.json";
import nodePublicationSummary from "./node-publication-summary.json";
import node from "./node.json";
import phenotypeExplorerCompare from "./phenotype-explorer-compare.json";
import phenotypeExplorerSearch from "./phenotype-explorer-search.json";
import search from "./search.json";
import textAnnotator from "./text-annotator.json";
import uptime from "./uptime.json";

/** make single regex from base url and pattern */
const regex = (base: string = "", pattern: string = "") =>
  new RegExp(base + pattern.replace(/[/\\]/g, "\\$&"), "i");

/** api calls to be mocked with fixture data */
export const handlers = [
  /** dynamically fetched data on /sources */
  rest.get(regex(biolink, "/metadata/datasets"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(datasets)),
  ),

  /** api status monitoring on /help */
  rest.post(regex(uptimeRobot), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(uptime)),
  ),

  /** histopheno data */
  rest.get(regex(monarch, "/histopheno"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(histopheno)),
  ),

  /** submit feedback form */
  rest.post(regex(feedbackEndpoint), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(feedback)),
  ),

  /** search * */
  rest.get(regex(monarch, "/search"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(search)),
  ),

  /** autocomplete */
  rest.get(regex(monarch, "/autocomplete"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(autocomplete)),
  ),

  /** text annotator */
  rest.post(regex(biolink, "/nlp/annotate"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(textAnnotator)),
  ),

  /** phenotype explorer */
  rest.get(regex(biolink, "/sim/search"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(phenotypeExplorerSearch)),
  ),
  rest.post(regex(monarch, "/semsim/compare"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(phenotypeExplorerCompare)),
  ),

  /** node associations */
  rest.get(regex(monarch, "/associations"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(associations)),
  ),

  /** node associations table */
  rest.get(regex(monarch, "/entity/.*/.*"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(associationsTable)),
  ),

  /** node lookup */
  rest.get(regex(monarch, "/entity/.*"), (req, res, ctx) => {
    /**
     * change fixture data based on request so we can see UI that is conditional
     * on name/category/etc
     */
    const id = req.url.pathname.match(/\/entity\/(.*)/)?.[1] || "";

    const replace: {
      [key: string]: { name?: string; category?: string };
    } = {
      "MONDO:0007523": {
        name: "Ehlers-Danlos syndrome, hypermobility",
        category: "biolink:Disease",
      },
      "HP:0100775": {
        name: "Dural ectasia",
        category: "biolink:Disease",
      },
      "HP:0003179": {
        name: "Protrusio acetabuli",
        category: "biolink:Disease",
      },
      "HP:0001083": {
        name: "Ectopia lentis",
        category: "biolink:Disease",
      },
      "HP:0000501": {
        name: "Glaucoma",
        category: "biolink:Disease",
      },
      "HP:0002705": {
        name: "High, narrow palate",
        category: "biolink:Disease",
      },
      "HP:0004382": {
        name: "Mitral valve calcification",
        category: "biolink:Disease",
      },
      "HP:0004326": {
        name: "Cachexia",
        category: "biolink:Disease",
      },
      "HP:0002816": {
        name: "Genu recurvatum",
        category: "biolink:Disease",
      },
      "HP:0004298": {
        name: "Abnormality of the abdominal wall",
        category: "biolink:Disease",
      },
      "HP:0002996": {
        name: "Limited elbow movement",
        category: "biolink:Disease",
      },
      "MONDO:0020208": {
        name: "syndromic myopia",
        category: "biolink:Disease",
      },
      "PMID:25614286": {
        category: "biolink:Publication",
      },
    };
    const { name, category } = replace[id] || {};
    node.id = id;
    if (name) node.name = name;
    if (category) node.category = category;

    return res(ctx.status(200), ctx.json(node));
  }),

  /** node publication info */
  rest.get(regex(esummary), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodePublicationSummary)),
  ),
  rest.get(regex(efetch), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodePublicationAbstract.abstract)),
  ),

  /** any other request */
  rest.get(/.*/, (req) => {
    console.info("Non-mocked request", req.url.pathname);
    return req.passthrough();
  }),
];
