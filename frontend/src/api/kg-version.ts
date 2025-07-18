import { apiUrl, request } from "@/api";

/** Each entry returned by GET /releases */
interface ReleaseEntry {
  version: string;
  url: string;
}

/**
 * Fetches the most recent Knowledge Graph release version.
 *
 * @async
 * @function getLatestKGReleaseDate
 * @returns {Promise<string>} A promise that resolves to the latest release
 *   version.
 * @throws {Error} If the API returns no releases.
 */
export const getLatestKGReleaseDate = async (): Promise<string> => {
  const url = `${apiUrl}/releases`;
  const releases = await request<ReleaseEntry[]>(url, { limit: 2 });
  if (!Array.isArray(releases) || releases.length === 0) {
    throw new Error("No KG releases found");
  }
  return releases[1].version;
};
