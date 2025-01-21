import { ref } from "vue";
import { pick } from "lodash";
import type { DirectionalAssociation, Node } from "@/api/model";
import { parse } from "@/util/object";

const breadcrumbKeys = ["id", "category", "name", "in_taxon_label"] as const;

export type BreadcrumbNode = Pick<Node, (typeof breadcrumbKeys)[number]>;

export type Breadcrumb = {
  /** node we're coming from */
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

export function toBreadcrumbNode(node: Node) {
  const obj: BreadcrumbNode = pick(node, breadcrumbKeys);
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
