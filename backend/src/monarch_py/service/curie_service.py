### make a singleton class that uses prefixmap and curies to expand curies

from prefixmaps import load_converter

__all__ = [
    "converter",
]

# Use the Monarch-specific clone of the "merged" prefixmap context. Aligns
# with kg-phenio's normalize step (also being moved to the same context to
# fix the FBBT/WBBT prefix-casing issue that was dropping ~503k Alliance
# gene-expression edges to dangling, see monarch-app#1319). Same canonical
# behavior as "merged" today; standardizes the Monarch-facing label across
# the stack.
# (https://github.com/linkml/prefixmaps/blob/main/src/prefixmaps/data/merged.monarch.csv)
converter = load_converter("merged.monarch")
converter.add_prefix("GARD", "https://rarediseases.info.nih.gov/diseases/")
converter.add_prefix("NORD", "https://rarediseases.org/?p=")
converter.add_prefix("Orphanet", "https://www.orpha.net/en/disease/detail/", merge=True)
# icd.codes is dead/returning 403s, override to use icd10data.com search
# (add_prefix merge only adds as synonym, so patch prefix_map directly)
converter.prefix_map["ICD10CM"] = "https://www.icd10data.com/search?s="
converter.add_prefix(
    "phenopacket.store",
    "https://github.com/monarch-initiative/phenopacket-store/blob/main/notebooks/",
)
