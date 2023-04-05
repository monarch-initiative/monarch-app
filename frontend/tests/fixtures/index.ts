import { rest } from "msw";

import { biolink } from "@/api";

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

/** api calls to be mocked with fixture data */
export const handlers = [
  /** dynamically fetched data on /sources */
  rest.get(/metadata\/datasets/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(datasets))
  ),

  rest.get(/obo.+ontologies/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(ontologies))
  ),

  /** api status monitoring on /help */
  rest.post(/api\.uptimerobot\.com/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(uptime))
  ),

  rest.get(/api\/entity\/\w+:/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(entity))
  ),

  rest.get(/api\/histopheno\/\w+:/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(histopheno))
  ),

  /** submit feedback form */
  rest.post(/monarch-gh-issue-post/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(feedback))
  ),

  /**
   * node autocomplete TODO: remove when autocomplete below is hooked up to
   * components
   */
  rest.get(/search\/entity\/autocomplete/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeAutocomplete))
  ),

  /** autocomplete */
  rest.get(/autocomplete?/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(autocomplete))
  ),

  /** node search - TODO: remove when new search below is hooked up to components */
  rest.get(/search\/entity/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeSearch))
  ),

  /** search * */
  rest.get(/api\/search?/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(search))
  ),

  /** text annotator */
  rest.post(/nlp\/annotate/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(textAnnotator))
  ),

  /** phenotype explorer */
  rest.get(/sim\/search/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(phenotypeExplorerSearch))
  ),

  rest.post(/sim\/compare/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(phenotypeExplorerCompare))
  ),

  /** raw node search (without provided category) */
  rest.get(/\/bioentity\/[^/]+$/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeLookup))
  ),

  /** node search */
  rest.get(/\/bioentity\/\w+\/[^/]+$/i, (req, res, ctx) => {
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
  rest.get(/mygene\.info/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeGene))
  ),

  /** node publication info */
  rest.get(/esummary\.fcgi/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodePublicationSummary))
  ),

  rest.get(/efetch\.fcgi/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodePublicationAbstract.abstract))
  ),

  /** node hierarchy info */
  rest.get(/graph\/edges\/from/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeHierarchy))
  ),

  /** node associations data */
  rest.get(/\/bioentity\/\w+\/[^/]+\/\w+.*$/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeAssociations))
  ),

  /** association evidence data */
  rest.get(/evidence\/graph/, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(associationEvidence))
  ),

  /** ontol get id from label */
  rest.post(/ontol\/identifier/, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(ontolIdentifier))
  ),

  /**
   * any other request that's not biolink, pass through (ignore) without warning
   * https://stackoverflow.com/questions/406230/regular-expression-to-match-a-line-that-doesnt-contain-a-word
   */
  rest.get(new RegExp(`^(?!${biolink}).*$`), (req) => req.passthrough()),
];
