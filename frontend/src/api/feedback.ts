import { request } from ".";

/** serverless endpoint to make post on helpdesk with github api */
const api =
  "https://us-central1-monarch-initiative.cloudfunctions.net/monarch-gh-issue-post";

interface _Success {
  html_url: string;
}

interface _Error {
  error: string;
  next_request: string;
}

/** status response (from backend) */
type _Response = _Success | _Error;

/** create issue on helpdesk on submit of feedback form */
export const postFeedback = async (
  title = "",
  body = ""
): Promise<IssueLink> => {
  /** check params */
  if (!title || !body) throw new Error("Title or body not specified");

  /** post to api endpoint which posts new github issue */
  const data = await request<_Response>(
    api,
    { title, body },
    { method: "POST" }
  );

  /** if error */
  if ("error" in data) throw new Error(data.error);

  /** if success */
  if ("html_url" in data) return data.html_url;

  /** last resort */
  throw new Error("Unknown problem submitting feedback");
};

/** link to posted issue (for frontend) */
type IssueLink = string;
