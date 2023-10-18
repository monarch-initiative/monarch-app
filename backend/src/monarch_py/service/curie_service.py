### make a singleton class that uses prefixmap and curies to expand curies

from curies import Converter
from prefixmaps.io.parser import load_multi_context


class CurieService:
    _instance = None
    converter: Converter

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurieService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        # this is a magic keyword that represents the "merged" context from Chris M's algorithm
        # (https://github.com/linkml/prefixmaps/blob/main/src/prefixmaps/data/merged.csv)
        context = load_multi_context(["merged"])
        extended_prefix_map = context.as_extended_prefix_map()
        self.converter = Converter.from_extended_prefix_map(extended_prefix_map)

    def expand(self, curie: str) -> str:
        return self.converter.expand(curie)
