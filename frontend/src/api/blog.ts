import { stripHtml } from "@/util/string";
import { request } from "./";

/** rss of monarch medium feed */
const monarchRss =
  "https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/@monarchinit";

/** items (from backend) */
type _BlogItems = {
  items: {
    title?: string;
    pubDate?: string;
    link?: string;
    thumbnail?: string;
    description?: string;
    content?: string;
    categories?: string[];
  }[];
};

/** get "blog" entries from monarch on medium.com */
export const getBlogPosts = async (): Promise<BlogItems> => {
  const { items } = await request<_BlogItems>(monarchRss);

  return items.map((item) => ({
    title: item.title || "",
    // The time is deliberately dropped, leaving a date-only string -- which parses as
    // UTC midnight and then renders as the previous day for viewers west of UTC. The
    // `T00:00:00` makes it local midnight instead, so the date a post is labelled with
    // is the date it shows. Publications reach AppPost already parsed this way.
    date: new Date(`${item.pubDate?.split(/\s/)[0]}T00:00:00`) || new Date(),
    link: item.link || "",
    thumbnail: item.thumbnail || "",
    description: stripHtml(item.description),
    tags: item.categories || [],
  }));
};

/** items (for frontend) */
type BlogItems = {
  title: string;
  date: Date;
  link: string;
  thumbnail: string;
  description: string;
  tags: string[];
}[];
