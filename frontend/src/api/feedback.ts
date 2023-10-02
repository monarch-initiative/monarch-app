import { stringify } from "@/util/object";
import { request } from "./";

/** serverless endpoint to make post on helpdesk with github api */
export const feedbackEndpoint =
  "https://us-central1-monarch-initiative.cloudfunctions.net/monarch-gh-issue-post";

/** status response (from backend) */
type _Response = {
  html_url: string;
};

/** create issue on helpdesk on submit of feedback form */
export const postFeedback = async (
  title = "",
  body = "",
): Promise<IssueLink> => {
  /** check if params blank */
  if (!title || !body) throw Error("Title or body not specified");

  /** make request options */
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");

  /** post to api endpoint which posts new github issue */
  const data = await request<_Response>(feedbackEndpoint, undefined, {
    method: "POST",
    headers,
    body: stringify({ title, body }),
  });

  return data.html_url;
};

/** link to posted issue (for frontend) */
type IssueLink = string;
