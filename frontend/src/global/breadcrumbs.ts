import { ref } from "vue";
import { Node } from "@/api/node-lookup";
import { Association } from "@/api/node-associations";
import { parse } from "@/util/object";

interface Breadcrumb {
  node: Node;
  relation: Association["relation"];
}

/** breadcrumbs object for breadcrumbs section on node page */
export const breadcrumbs = ref<Array<Breadcrumb>>([]);

/** keep breadcrumbs global variable in sync with history.state.breadcrumbs */
export const updateBreadcrumbs = () =>
  (breadcrumbs.value = parse(window.history.state?.breadcrumbs, []));
