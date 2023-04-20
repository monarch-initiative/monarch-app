import { stripHtml } from "@/util/string";
import { request } from "./";

/** rss of monarch medium feed */
const monarchRss =
  "https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/@monarchinit";

/** items (from backend) */
interface _BlogItems {
  items: Array<{
    title?: string;
    pubDate?: string;
    link?: string;
    thumbnail?: string;
    description?: string;
    content?: string;
    categories?: Array<string>;
  }>;
}

/** get "blog" entries from monarch on medium.com */
export const getBlogPosts = async (): Promise<BlogItems> => {
  const { items } = await request<_BlogItems>(monarchRss);

  return items.map((item) => ({
    title: item.title || "",
    date: new Date(item.pubDate?.split(/\s/)[0] || "") || new Date(),
    link: item.link || "",
    thumbnail: item.thumbnail || "",
    description: stripHtml(item.description),
    tags: item.categories || [],
  }));
};

/** items (for frontend) */
type BlogItems = Array<{
  title: string;
  date: Date;
  link: string;
  thumbnail: string;
  description: string;
  tags: Array<string>;
}>;
