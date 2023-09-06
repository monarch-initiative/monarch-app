import { groupLog } from "@/util/debug";
import { getUrl } from "@/util/url";

/** base biolink api url */
export const biolink = "https://api.monarchinitiative.org/api";

/** served location of web app, from address bar or storage redirect */
const url = new URL(window.sessionStorage.redirectHref || window.location.href);

/** get monarch api name/version to use */

/** infer as best as possible from url */
let fromDomain =
  /** sub domain */
  url.hostname.match(/([\w\d-]+)?\.?(monarchinitiative)\.org/)?.[1] || "";

/** production url */
if (url.hostname === "monarchinitiative.org") fromDomain = "production";

/** running web app locally */
if (url.hostname === "localhost")
  // fromDomain = "local";
  fromDomain = "next";

/** netlify pr deploy previews */
if (url.hostname.endsWith("netlify.app")) fromDomain = "next";

/** specific ip */
if (url.hostname.match(/\d+\.\d+\.\d+\.\d+/)) fromDomain = "relative";

/** last resort fallback */
if (!fromDomain) fromDomain = "next";

/** from env var */
const fromEnv = import.meta.env.VITE_API || "";

/** from param in url */
const fromParam = new URLSearchParams(url.search).get("api") || "";

/** name of monarch api version to use. highest to lowest override priority. */
export const apiName = fromParam || fromEnv || fromDomain;

/** api url suffix */
const suffix = "/v3/api";

/** base monarch api url */
let monarch = `https://api-${apiName}.monarchinitiative.org${suffix}`;

/** production version */
if (apiName === "production")
  monarch = `https://api.monarchinitiative.org${suffix}`;

/** relative to wherever web app is hosted */
if (apiName === "relative") monarch = suffix;

/** locally running server */
if (apiName === "local") monarch = `127.0.0.1:8000${suffix}`;

export { monarch };

groupLog(`API version: ${apiName}`, {
  fromParam,
  fromEnv,
  fromDomain,
  apiName,
  monarch,
});

type Param = string | number | boolean | undefined | null;
export type Params = { [key: string]: Param | Param[] };

/** session response cache */
const cache = new Map<string, Response>();

/** generic fetch request wrapper */
export const request = async <Response>(
  /** request url */
  path = "",
  /**
   * key/value object for url parameters. use primitive for single, array for
   * multiple/duplicate.
   *
   * { ids: "1,2,3" } -> ?ids=1,2,3
   *
   * { id: [1,2,3] } -> ?id=1&id=2&id=3
   */
  params: Params = {},
  /** fetch options */
  options: RequestInit = {},
  /** parse response mode */
  parse: "text" | "json" = "json",
): Promise<Response> => {
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

  /** make request object */
  const request = new Request(url, options);

  /** unique request id */
  const id = JSON.stringify(request, ["url", "method", "headers"]);

  /** first check if request is cached */
  let response = cache.get(id);

  /** logging info */
  const cached = response ? "cached" : "new";
  const endpoint = getUrl(path, "pathname").replace(suffix, "");

  if (import.meta.env.MODE !== "test")
    groupLog(`📞 Request (${cached}) ${endpoint}`, {
      url,
      params,
      options,
      request,
    });

  /** if request not cached */
  if (!response)
    /* make new request */
    response = await fetch(url, options);

  /** check response code */
  if (!response.ok) throw new Error(`Response not OK`);

  /** add response to cache */
  if (request.method === "GET") cache.set(id, response.clone());

  /** parse response */
  const parsed: Response =
    parse === "text" ? await response.text() : await response.json();

  if (import.meta.env.MODE !== "test")
    groupLog(`📣 Response (${cached}) ${endpoint}`, {
      url,
      params,
      options,
      parsed,
      response,
    });

  return parsed;
};
