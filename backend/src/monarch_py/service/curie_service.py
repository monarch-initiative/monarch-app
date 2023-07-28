### make a singleton class that uses prefixmap and curies to expand curies

import curies
from curies import Converter


class CurieService:
    _instance = None
    converter: Converter

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurieService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.converter = curies.get_monarch_converter()

    def expand(self, curie: str) -> str:
        return self.converter.expand(curie)
