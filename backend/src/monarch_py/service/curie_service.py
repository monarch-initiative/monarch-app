### make a singleton class that uses prefixmap and curies to expand curies

from prefixmaps import load_converter

__all__ = [
    "converter",
]

# this is a magic keyword that represents the "merged" context from Chris M's algorithm
# (https://github.com/linkml/prefixmaps/blob/main/src/prefixmaps/data/merged.csv)
converter = load_converter(["merged"])
