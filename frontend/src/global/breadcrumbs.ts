import { ref } from "vue";
import type { DirectionalAssociation, Node } from "@/api/model";
import { parse } from "@/util/object";

export type Breadcrumb = {
  node: Partial<Node>;
  association: Partial<DirectionalAssociation>;
};

/** breadcrumbs object for breadcrumbs section on node page */
export const breadcrumbs = ref<Breadcrumb[]>([]);

/** keep breadcrumbs global variable in sync with history.state.breadcrumbs */
export const updateBreadcrumbs = () =>
  (breadcrumbs.value = parse<Breadcrumb[]>(
    window.history.state?.breadcrumbs,
    [],
  ));
