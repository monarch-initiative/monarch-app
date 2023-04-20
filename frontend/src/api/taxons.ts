import { values } from "lodash";
import { biolink, request } from "./index";

/** taxon ids (from backend) */
type _Ids = { [key: string]:  string[] };

/** from list of taxon labels, get list of matching taxon ids */
export const getIdsFromLabels = async (ids: string[]): Promise<Ids> => {
  const url = `${biolink}/ontol/identifier`;
  const params = { label: ids };
  const options = { method: "POST" };
  const response = await request<_Ids>(url, params, options);

  return (
    values(response)
      .map(
        /** list of ids that match this label */
        (ids) =>
          /** prefer ncbi id */
          ids.find((id) => id.includes("NCBITaxon")) ||
          /** fallback to first id */
          ids[0]
      )
      /** filter out no match */
      .filter((id) => id)
  );
};

/** taxon ids (for frontend) */
type Ids = string[];
