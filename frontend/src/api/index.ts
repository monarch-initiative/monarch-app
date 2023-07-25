/** base biolink api url */
export const biolink = "https://api.monarchinitiative.org/api";

/** served location of webapp, verbatim from browser address bar */
const url = new URL(window.location.href);

/** get api name to use... */

/** ...from domain of url */
const fromDomain =
  /** when running yarn dev */
  (url.port && "local") ||
  /** get from subdomain */
  url.hostname.match(/([/w-]+)?\.?(monarchinitiative)\.org/)?.[1] ||
  /** prod url has no subdomain */
  "prod";

/** ...from env var */
const fromEnv = import.meta.env.VITE_API || "";

/** ...from param in url */
const fromParam = new URLSearchParams(url.href).get("api") || "";

/**
 * final short name of monarch api version to use (highest to lowest override
 * priority)
 */
export const apiName = fromParam || fromEnv || fromDomain;

/** get full api url from short name */
const apiMap: { [key: string]: string } = {
  local: "127.0.0.1:8000",
  dev: "https://api-dev.monarchinitiative.org",
  beta: "https://api-beta.monarchinitiative.org",
  prod: "https://api-dev.monarchinitiative.org/v3/api",
};

/** base monarch api url */
export const monarch = apiMap[apiName] || apiMap.dev;

/**
 * key/value object for request query parameters. use primitive for single, e.g.
 * evidence=true. use array for multiple/duplicate, e.g. id=abc&id=def&id=ghi
 */
type Param = string | number | boolean | undefined | null;
export type Params = { [key: string]: Param | Param[] };

/**
 * generic fetch request wrapper
 *
 * @param path request url
 * @param params url params. { param: [1,2,3] } becomes ?param=1&param=2&param=3
 *   { param: "1,2,3" } stays ?param=1,2,3
 * @param options fetch() options
 * @param parse parse response mode
 */
export const request = async <Response>(
  path = "",
  params: Params = {},
  options: RequestInit = {},
  parse: "text" | "json" = "json",
): Promise<Response> => {
  /** start cache if not already started */
  if (!cache) await initCache();

  /** get string of url parameters/options */
  const paramsObject = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    const values = [value].flat();
    for (const value of values)
      if (["string", "number", "boolean"].includes(typeof value))
        paramsObject.append(key, String(value));
  }

  /** sort params for consistency */
  paramsObject.sort();

  /** assemble url to query */
  const paramsString = "?" + paramsObject.toString();
  const url = path + paramsString;

  /** endpoint for logging */
  let endpoint = path;
  if (endpoint.startsWith(biolink))
    endpoint = endpoint.replace(biolink, "biolink ");
  if (endpoint.startsWith(monarch))
    endpoint = endpoint.replace(monarch, "monarch ");

  /** make request object */
  const request = new Request(url, options);

  /** first check if request is cached */
  let response = await cache.match(request);

  /** log details for debugging (except don't clutter logs when running tests) */
  if (import.meta.env.MODE !== "test") {
    console.groupCollapsed(
      response ? "📞 Request (cached)" : "📞 Request (new)",
      endpoint,
    );
    console.info("Url", url);
    console.info("Params", params);
    console.info("Options", options);
    console.info("Request", request);
    console.groupEnd();
  }

  /** if request not cached */
  if (!response) {
    /** make new request */
    response = await fetch(url, options);

    /** check response code */
    if (!response.ok) {
      /** get biolink error message, if there is one */
      let message;
      try {
        message = ((await response.json()) as BioLinkError).error.message;
      } catch (error) {
        message = "";
      }
      throw new Error(message || `Response not OK`);
    }

    /**
     * add response to cache (if GET,
     * https://w3c.github.io/ServiceWorker/#cache-put)
     */
    if (request.method === "GET") await cache.put(request, response.clone());
  }

  /** parse response */
  const parsed: Response =
    parse === "text" ? await response.text() : await response.json();

  /** log details for debugging (except don't clutter logs when running tests) */
  if (import.meta.env.MODE !== "test") {
    console.groupCollapsed("📣 Response", endpoint);
    console.info("Url", url);
    console.info("Parsed", parsed);
    console.info("Response", response);
    console.groupEnd();
  }

  return parsed;
};

/** cache interface */
let cache: Cache;
const name = "monarch-cache";

/** start cache */
const initCache = async () => {
  /** start fresh each session (as if using sessionStorage) */
  await window.caches.delete(name);
  /** set cache interface */
  cache = await window.caches.open(name);
};

/** possible biolink error */
type BioLinkError = {
  error: {
    message: string;
  };
};

/**
 * create dummy caches interface. only really needed for local mobile testing so
 * requests don't error.
 * https://stackoverflow.com/questions/53094298/window-caches-is-undefined-in-android-chrome-but-is-available-at-desktop-chrome
 */
if (!window.caches) {
  window.caches = {
    open: async () => ({
      match: (async () => undefined) as Cache["match"],
      put: (async () => undefined) as Cache["put"],
    }),
    delete: (async () => true) as CacheStorage["delete"],
  } as unknown as CacheStorage;
}
