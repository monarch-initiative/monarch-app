/** base api url */
export const biolink = "https://api.monarchinitiative.org/api";
export const monarch = "https://api-dev.monarchinitiative.org/api";

/**
 * key/value object for request query parameters. use primitive for single, e.g.
 * evidence=true. use array for multiple/duplicate, e.g. id=abc&id=def&id=ghi
 */
type Param = string | number | boolean | undefined | null;
export type Params = Record<string, Param | Param[]>;

/**
 * generic fetch request wrapper
 *
 * @param path request url
 * @param params url params
 * @param options fetch() options
 * @param parse parse response mode
 */
export const request = async <T>(
  path = "",
  params: Params = {},
  options: RequestInit = {},
  parse: "text" | "json" = "json"
): Promise<T> => {
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
  const endpoint = path.replace(biolink, "");

  /** make request object */
  const request = new Request(url, options);

  /** first check if request is cached */
  let response = await cache.match(request);

  /** log details for debugging (except don't clutter logs when running tests) */
  if (import.meta.env.NODE_ENV !== "test") {
    console.groupCollapsed(
      response ? "Using cached request" : "Making new request",
      endpoint
    );
    console.info({ params, options, request });
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
        message = ((await response.json()) as _Error).error.message;
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
  const parsed =
    parse === "text"
      ? ((await response.text()) as unknown as T)
      : await response.json();

  /** log details for debugging (except don't clutter logs when running tests) */
  if (import.meta.env.NODE_ENV !== "test") {
    console.groupCollapsed("Response", endpoint);
    console.info({ parsed, response });
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
type _Error = {
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
