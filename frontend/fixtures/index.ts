import { rest } from "msw";
/** url bases */
import { biolink, monarch } from "@/api";
import { feedbackEndpoint } from "@/api/feedback";
import { mygeneinfo } from "@/api/genes";
import { obo } from "@/api/ontologies";
import { efetch, esummary } from "@/api/publications";
import { uptimeRobot } from "@/api/uptime";
import associationEvidence from "./association-evidence.json";
import autocomplete from "./autocomplete.json";
import datasets from "./datasets.json";
import entity from "./entity.json";
import feedback from "./feedback.json";
import histopheno from "./histopheno.json";
import nodeAssociations from "./node-associations.json";
import nodeAutocomplete from "./node-autocomplete.json";
import nodeGene from "./node-gene.json";
import nodeHierarchy from "./node-hierarchy.json";
import nodeLookup from "./node-lookup.json";
import nodePublicationAbstract from "./node-publication-abstract.json";
import nodePublicationSummary from "./node-publication-summary.json";
import nodeSearch from "./node-search.json";
import ontolIdentifier from "./ontol-identifier.json";
import ontologies from "./ontologies.json";
import phenotypeExplorerCompare from "./phenotype-explorer-compare.json";
import phenotypeExplorerSearch from "./phenotype-explorer-search.json";
import search from "./search.json";
import textAnnotator from "./text-annotator.json";
import uptime from "./uptime.json";

/** allow typing in regular string for basic api url paths */
/** https://stackoverflow.com/questions/3446170/escape-string-for-use-in-javascript-regex */
const escapeRegex = (string = "") =>
  string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** make single regex from base url and pattern */
const regex = (base: string = "", pattern: string | RegExp = "") =>
  new RegExp(
    base +
      (typeof pattern === "string" ? escapeRegex(pattern) : pattern.source),
    "i"
  );

/** api calls to be mocked with fixture data */
export const handlers = [
  /** dynamically fetched data on /sources */
  rest.get(regex(biolink, "/metadata/datasets"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(datasets))
  ),

  rest.get(regex(obo), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(ontologies))
  ),

  /** api status monitoring on /help */
  rest.post(regex(uptimeRobot), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(uptime))
  ),

  /** entity lookup */
  rest.get(regex(monarch, "/entity"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(entity))
  ),

  /** histopheno data */
  rest.get(regex(monarch, "/histopheno"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(histopheno))
  ),

  /** submit feedback form */
  rest.post(regex(feedbackEndpoint), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(feedback))
  ),

  /**
   * node autocomplete TODO: remove when autocomplete below is hooked up to
   * components
   */
  rest.get(regex(biolink, "/search/entity/autocomplete"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeAutocomplete))
  ),

  /** autocomplete */
  rest.get(regex(monarch, "/autocomplete"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(autocomplete))
  ),

  /** node search - TODO: remove when new search below is hooked up to components */
  rest.get(regex(biolink, "/search/entity"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeSearch))
  ),

  /** search * */
  rest.get(regex(monarch, "/search"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(search))
  ),

  /** text annotator */
  rest.post(regex(biolink, "/nlp/annotate"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(textAnnotator))
  ),

  /** phenotype explorer */
  rest.get(regex(biolink, "/sim/search"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(phenotypeExplorerSearch))
  ),

  rest.post(regex(biolink, "/sim/compare"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(phenotypeExplorerCompare))
  ),

  /** raw node search (without provided category) */
  rest.get(regex(biolink, /\/bioentity\/[^/]+$/), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeLookup))
  ),

  /** node search */
  rest.get(regex(biolink, /\/bioentity\/\w+\/[^/]+$/), (req, res, ctx) => {
    /**
     * change fixture data based on request so we can see UI that is conditional
     * on name/category/etc
     */
    const [, category = "", id = ""] =
      req.url.pathname.match(/\/bioentity\/(\w+)\/(.+)\\?/) || [];
    const labels: Record<string, string> = {
      "MONDO:0007947": "Marfan syndrome",
      "HP:0100775": "Dural ectasia",
      "HP:0003179": "Protrusio acetabuli",
      "HP:0001083": "Ectopia lentis",
      "HP:0000501": "Glaucoma",
      "HP:0002705": "High, narrow palate",
      "HP:0004382": "Mitral valve calcification",
      "HP:0004326": "Cachexia",
      "HP:0002816": "Genu recurvatum",
      "HP:0004298": "Abnormality of the abdominal wall",
      "HP:0002996": "Limited elbow movement",
      "MONDO:0020208": "syndromic myopia",
    };
    nodeLookup.label = labels[id] || "Marfan syndrome";
    nodeLookup.category = [category];
    /**
     * note that this will show (in yarn test:gui) silly things like "Marfan
     * syndrome: gene", because only the category field is changed
     */

    return res(ctx.status(200), ctx.json(nodeLookup));
  }),

  /** node gene info */
  rest.get(regex(mygeneinfo), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeGene))
  ),

  /** node publication info */
  rest.get(regex(esummary), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodePublicationSummary))
  ),

  rest.get(regex(efetch), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodePublicationAbstract.abstract))
  ),

  /** node hierarchy info */
  rest.get(regex(biolink, "/graph/edges/from"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeHierarchy))
  ),

  /** node associations data */
  rest.get(regex(biolink, /\/bioentity\/\w+\/[^/]+\/\w+.*$/), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeAssociations))
  ),

  /** association evidence data */
  rest.get(regex(biolink, "/evidence/graph"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(associationEvidence))
  ),

  /** ontol get id from label */
  rest.post(regex(biolink, "/ontol/identifier"), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(ontolIdentifier))
  ),

  /** any other request */
  rest.get(/.*/, (req, res, ctx) => {
    /** for certain exceptions, passthrough (let browser make a real request) */
    const exceptions = [
      ".vue",
      ".mp4",
      ".svg",
      ".png",
      ".jpg",
      ".jpeg",
      ".gif",
      ".bmp",
      ".tiff",
      ".woff",
      ".json",
      ".jsonld",
      ".txt",
      "site.webmanifest",
      "medium.com",
      "fonts.googleapis.com",
    ];
    if (exceptions.some((exception) => req.url.href.includes(exception)))
      return req.passthrough();

    /**
     * otherwise, throw error to make sure we never hit any api when mocking is
     * enabled
     */
    return res(ctx.status(500, "Non-mocked request"));
  }),
];
