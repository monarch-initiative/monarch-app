/**
 * Google Form used to request an invite to the Monarch Initiative Slack
 * workspace.
 */
export const MONARCH_SLACK_SIGNUP_FORM_URL =
  "https://docs.google.com/forms/d/e/1FAIpQLSf0hOZv6UMW6PD1sRtK74OQLV8ZA8nFRICo0T0ngb2IKFBh5A/viewform";

export type CommunitySocialIconType =
  | "email"
  | "slack"
  | "medium"
  | "github"
  | "linkedin"
  | "youtube"
  | "bluesky";

export interface CommunitySocialLink {
  id: string;
  /** Passed to `AppSocialIcon` and used for chip styling where relevant */
  socialIconType: CommunitySocialIconType;
  /** `AppIcon` name (Font Awesome or `assets/icons` SVG) */
  icon: string;
  url: string;
  /** Footer / Contact `v-tooltip` */
  tooltip: string;
  /** When set, this row also appears in the header Community dropdown */
  nav?: { key: string; label: string };
}

/**
 * Social / community links shown on Get Involved, footer, and Contact (same
 * order). Subset with `nav` populate the Community menu after “Get Involved”.
 */
export const COMMUNITY_SOCIAL_LINKS: CommunitySocialLink[] = [
  {
    id: "friends-mail",
    socialIconType: "email",
    icon: "envelope",
    url: "https://groups.google.com/g/monarch-friends/",
    tooltip: "Subscribe",
  },
  {
    id: "slack",
    socialIconType: "slack",
    icon: "social-slack",
    url: MONARCH_SLACK_SIGNUP_FORM_URL,
    tooltip: "Slack",
    nav: { key: "community-slack", label: "Slack" },
  },
  {
    id: "medium",
    socialIconType: "medium",
    icon: "medium",
    url: "https://monarchinit.medium.com",
    tooltip: "Medium",
    nav: { key: "community-blog", label: "Blog" },
  },
  {
    id: "github",
    socialIconType: "github",
    icon: "github",
    url: "https://github.com/monarch-initiative",
    tooltip: "GitHub",
  },
  {
    id: "linkedin",
    socialIconType: "linkedin",
    icon: "linkedin",
    url: "https://www.linkedin.com/company/the-monarch-initiative",
    tooltip: "LinkedIn",
    nav: { key: "community-linkedin", label: "LinkedIn" },
  },
  {
    id: "youtube",
    socialIconType: "youtube",
    icon: "youtube",
    url: "https://www.youtube.com/@monarchinitiative",
    tooltip: "YouTube",
    nav: { key: "community-youtube", label: "YouTube" },
  },
  {
    id: "bluesky",
    socialIconType: "bluesky",
    icon: "social-bluesky",
    url: "https://bsky.app/profile/monarchinitiative.bsky.social",
    tooltip: "Bluesky",
    nav: { key: "community-bluesky", label: "Bluesky" },
  },
];

const COMMUNITY_NAV_EXTERNAL_ORDER = [
  "slack",
  "medium",
  "linkedin",
  "youtube",
  "bluesky",
] as const;

/**
 * Header/footer `Community` column (dropdown), including “Get Involved” +
 * external links.
 */
export function getCommunityNavSection() {
  const external = COMMUNITY_NAV_EXTERNAL_ORDER.map((id) => {
    const link = COMMUNITY_SOCIAL_LINKS.find((l) => l.id === id);
    if (!link?.nav) {
      throw new Error(`community nav: missing link or nav for id "${id}"`);
    }
    return {
      label: link.nav.label,
      key: link.nav.key,
      to: link.url,
      icon: true,
    };
  });

  return {
    label: "Community",
    subItems: [
      {
        label: "Get Involved",
        key: "community-get-involved",
        to: "/community/get-involved",
      },
      ...external,
    ],
  };
}
