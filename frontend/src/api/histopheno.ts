import { apiUrl, request } from "./index";
import type { HistoPheno } from "./model";

export const getHistoPheno = async (id: string): Promise<HistoPheno> => {
  const url = `${apiUrl}/histopheno/${id}`;
  const response = await request<HistoPheno>(url);
  return response;
};
