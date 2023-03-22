import { monarch, request } from "./index";
import { HistoPheno } from "./model";

export const getHistoPheno = async (id: string): Promise<HistoPheno> => {
  const url = `${monarch}/histopheno/${id}`;
  const response = await request<HistoPheno>(url);
  return response;
};
