// src/composables/usePhenotypeSets.ts
import { computed, ref } from "vue";
import { isEqual } from "lodash";
import type { Option, Options } from "@/components/AppSelectTags.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { arrayParam, useParam, type Param } from "@/composables/use-param";
import examples from "@/data/phenotype-explorer.json";

type GeneratedFrom = {
  option?: Option;
  options?: Options;
};
const optionParam: Param<Option> = {
  parse: (value) => ({ id: value }),
  stringify: (value) => String(value.id),
};
const optionsParam = arrayParam<Option>({
  parse: (value) => (value ? { id: value } : undefined),
  stringify: (value) => String(value.id),
});
export function usePhenotypeSets() {
  /** first set of phenotypes */
  const aPhenotypes = useParam<Options>("a-set", optionsParam, []);
  /** second set of phenotypes */
  const bPhenotypes = useParam<Options>("b-set", optionsParam, []);

  /** "generated from" helpers after selecting gene or disease */
  const aGeneratedFrom = ref<GeneratedFrom>({});
  const bGeneratedFrom = ref<GeneratedFrom>({});

  /** get description to show below phenotypes select box */
  function description(phenotypes: Options, generatedFrom: GeneratedFrom) {
    const description = [`${phenotypes.length} phenotypes`];
    if (isEqual(generatedFrom.options, phenotypes)) {
      description.push(
        `generated from "${generatedFrom.option?.label || generatedFrom.option?.id}"`,
      );
    }
    return `(${description.join(", ")})`;
  }

  /** when multi select component runs spread options function */
  function spreadOptions(option: Option, options: Options, set: "a" | "b") {
    if (options.length === 0) snackbar("No associated phenotypes found");
    else snackbar(`Selected ${options.length} phenotypes`);

    const generated = { option, options };
    if (set === "a") aGeneratedFrom.value = generated;
    else bGeneratedFrom.value = generated;
  }

  function doExample(type: "simple" | "bigger") {
    if (type === "simple") {
      aPhenotypes.value = examples.a.options;
      bPhenotypes.value = examples.b.options;
      aGeneratedFrom.value = examples.a;
      bGeneratedFrom.value = examples.b;
    } else {
      aPhenotypes.value = examples.c.options;
      bPhenotypes.value = examples.d.options;
      aGeneratedFrom.value = examples.c;
      bGeneratedFrom.value = examples.d;
    }
  }

  return {
    aPhenotypes,
    bPhenotypes,
    aGeneratedFrom,
    bGeneratedFrom,
    description,
    spreadOptions,
    doExample,
  };
}
