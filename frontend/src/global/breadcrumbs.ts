import { ref } from "vue";
import type { Association } from "@/api/node-associations";
import type { Node } from "@/api/node-lookup";
import { parse } from "@/util/object";

type Breadcrumb = {
  node: Node;
  relation: Association["relation"];
};

/** breadcrumbs object for breadcrumbs section on node page */
export const breadcrumbs = ref<Breadcrumb[]>([]);

/** keep breadcrumbs global variable in sync with history.state.breadcrumbs */
export const updateBreadcrumbs = () =>
  (breadcrumbs.value = parse(window.history.state?.breadcrumbs, []));
