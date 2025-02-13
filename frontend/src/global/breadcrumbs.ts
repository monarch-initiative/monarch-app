import { ref } from "vue";
import { pick } from "lodash";
import type { DirectionalAssociation, Node } from "@/api/model";
import { parse } from "@/util/object";

/**
 * This constant represents the minimal set of properties needed to render a
 * link to a Node object. If more properties must be added to render such a link
 * in the future, add them to this list.
 *
 * This is necessary because some pages render a large number of links to nodes.
 * Each node then must be serialized and inserted into the DOM by Vue. If the
 * size of nodes is non-trivial (as in, having lots of related nodes, which is
 * not uncommon), then serializing more than ~50 nodes would cause noticeable
 * slowdown in the UI. Rendering 1000 nodes would cause the browser to hang for
 * about a minute.
 *
 * To see the issue that initiated this, see:
 * https://github.com/monarch-initiative/monarch-app/issues/912
 */
const BREADCRUMB_KEYS = ["id", "category", "name", "in_taxon_label"] as const;

export type BreadcrumbNode = Pick<Node, (typeof BREADCRUMB_KEYS)[number]>;

export type Breadcrumb = {
  /* node we're coming from, represented as a small subset of keys defined above */
  node: BreadcrumbNode;

  /** association between the previous node and the current node */
  association: Partial<DirectionalAssociation>;

  /**
   * whether breadcrumb doesn't have its own history entry (e.g. implicitly
   * created sub-class association between current node and association
   * subject)
   */
  noEntry?: boolean;
};

/* Filter out properties of a node to only include those necessary to render a breadcrumb */
export function toBreadcrumbNode(node: Node) {
  const obj: BreadcrumbNode = pick(node, BREADCRUMB_KEYS);
  return obj;
}

/** breadcrumbs object for breadcrumbs section on node page */
export const breadcrumbs = ref<Breadcrumb[]>([]);

/** keep breadcrumbs global variable in sync with history.state.breadcrumbs */
export const updateBreadcrumbs = () =>
  (breadcrumbs.value = parse<Breadcrumb[]>(
    window.history.state?.breadcrumbs,
    [],
  ));
