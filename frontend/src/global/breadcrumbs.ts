import { ref } from "vue";
import type { Association, Node } from "@/api/model";
import { parse } from "@/util/object";

type Breadcrumb = {
  node: Node;
  predicate: Association["predicate"];
};

/** breadcrumbs object for breadcrumbs section on node page */
export const breadcrumbs = ref<Breadcrumb[]>([]);

/** keep breadcrumbs global variable in sync with history.state.breadcrumbs */
export const updateBreadcrumbs = () =>
  (breadcrumbs.value = parse(window.history.state?.breadcrumbs, []));
