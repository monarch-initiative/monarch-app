### make a singleton class that uses prefixmap and curies to expand curies

from curies import Converter
from prefixmaps import load_converter


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
        self.converter = load_converter(["merged"])

    def expand(self, curie: str) -> str:
        return self.converter.expand(curie)
