import { apiUrl, request } from "@/api";

/** Response from GET /version */
interface VersionResponse {
  monarch_kg_version: string;
  monarch_api_version: string;
  monarch_kg_source: string;
}

// Fetches the latest Knowledge Graph release version
export const getLatestKGReleaseDate = async (): Promise<string> => {
  const url = `${apiUrl}/version`;
  const versionInfo = await request<VersionResponse>(url);
  if (!versionInfo || !versionInfo.monarch_kg_version) {
    throw new Error("No KG version found");
  }
  return versionInfo.monarch_kg_version;
};

// Fetches the Knowledge Graph source URL
export const getKGSourceUrl = async (): Promise<string> => {
  const url = `${apiUrl}/version`;
  const versionInfo = await request<VersionResponse>(url);
  if (!versionInfo || !versionInfo.monarch_kg_source) {
    throw new Error("No KG source URL found");
  }
  return versionInfo.monarch_kg_source;
};
