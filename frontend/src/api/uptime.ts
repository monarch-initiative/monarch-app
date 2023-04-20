import type { Code } from "@/components/AppStatus.vue";
import { request } from "./";

/** https://uptimerobot.com/api/ */

/** Uptimerobot api endpoint */
const uptimeRobot = "https://api.uptimerobot.com/v2/getMonitors";
/** Read-only api key, safe to be distributed */
const key = "ur1488940-1c05ba09e0aef926989d6593";
/** Uptimerobot.org page for statuses */
const page = "https://stats.uptimerobot.com/XPRo9s4BJ5";

/** Uptime responses (from backend) */
type _Uptimes = {
  monitors?: {
    id?: string;
    friendly_name?: string;
    status?: _Code;
  }[];
};

/** Possible status codes (from backend) */
enum _Code {
  paused = 0,
  unchecked = 1,
  up = 2,
  seems_down = 8,
  down = 9,
}

/** Get list of uptimerobot monitors and their statuses, names, and other info */
export const getUptimes = async (): Promise<Uptimes> => {
  /** Get data from endpoint */
  const params = { api_key: key };
  const options = { method: "POST" };
  const response = await request<_Uptimes>(uptimeRobot, params, options);
  const { monitors = [] } = response;

  /**
   * Map uptimerobot status codes to our simplified status codes in status
   * component
   */
  const codeMap: Record<_Code | number, Code> = {
    [_Code.paused]: "paused",
    [_Code.unchecked]: "unknown",
    [_Code.up]: "success",
    [_Code.seems_down]: "error",
    [_Code.down]: "error",
  };

  /** Convert results to desired format */
  const results = monitors.map((monitor) => ({
    code: codeMap[Number(monitor.status)] || "unknown",
    text: monitor.friendly_name || "",
    link: page + "/" + (monitor.id || ""),
  }));

  return results;
};

/** Uptimes (for frontend) */
export type Uptimes = {
  code: Code;
  text: string;
  link: string;
}[];
