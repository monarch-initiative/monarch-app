/// <reference types="vite/client" />

declare module "phenogrid" {
  import type { PhenogridDefinition } from "@/api/phenogrid";
  const phenogrid: PhenogridDefinition;
  export default phenogrid;
}
