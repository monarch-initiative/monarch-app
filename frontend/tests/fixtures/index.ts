import { rest } from "msw";

import { biolink } from "@/api";

import datasets from "./datasets.json";
import ontologies from "./ontologies.json";
import uptime from "./uptime.json";
import entity from "./entity.json";
import feedback from "./feedback.json";
import nodeAutocomplete from "./node-autocomplete.json";
import nodeSearch from "./node-search.json";
import textAnnotator from "./text-annotator.json";
import phenotypeExplorerSearch from "./phenotype-explorer-search.json";
import phenotypeExplorerCompare from "./phenotype-explorer-compare.json";
import nodeLookup from "./node-lookup.json";
import nodeGene from "./node-gene.json";
import nodePublicationSummary from "./node-publication-summary.json";
import nodePublicationAbstract from "./node-publication-abstract.json";
import nodeHierarchy from "./node-hierarchy.json";
import nodeAssociations from "./node-associations.json";
import associationEvidence from "./association-evidence.json";
import ontolIdentifier from "./ontol-identifier.json";

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

  /** submit feedback form */
  rest.post(/monarch-gh-issue-post/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(feedback))
  ),

  /** node autocomplete */
  rest.get(/search\/entity\/autocomplete/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeAutocomplete))
  ),

  /** node search */
  rest.get(/search\/entity/i, (req, res, ctx) =>
    res(ctx.status(200), ctx.json(nodeSearch))
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
