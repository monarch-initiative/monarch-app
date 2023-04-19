import type { Plugin } from "vue";
import router from "@/router";
import tippy from "vue-tippy";
import "tippy.js/dist/tippy.css";
import "tippy.js/dist/border.css";
import { options } from "./tooltip";

/** List of global plugins and their options */
const plugins: Array<[Plugin, unknown]> = [
  [router, {}],
  [tippy, options],
];

export default plugins;
