import { ref } from "vue";
import type { DirectionalAssociation, Node } from "@/api/model";
import { parse } from "@/util/object";

export type Breadcrumb = {
  /** node we're coming from */
  node: Partial<Node>;
  /** association between the previous node and the current node */
  association: Partial<DirectionalAssociation>;
  /**
   * whether breadcrumb doesn't have its own history entry (e.g. implicitly
   * created sub-class association between current node and association
   * subject)
   */
  noEntry?: boolean;
};

/** breadcrumbs object for breadcrumbs section on node page */
export const breadcrumbs = ref<Breadcrumb[]>([]);

/** keep breadcrumbs global variable in sync with history.state.breadcrumbs */
export const updateBreadcrumbs = () =>
  (breadcrumbs.value = parse<Breadcrumb[]>(
    window.history.state?.breadcrumbs,
    [],
  ));
