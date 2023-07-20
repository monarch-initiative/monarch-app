### make a singleton class that uses prefixmap and curies to expand curies

from prefixmaps.io.parser import load_multi_context
from prefixmaps.datamodel.context import Context
from curies import Converter


class CurieService:
    _instance = None
    context: Context
    converter: Converter

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurieService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.context = load_multi_context(["merged"])
        # self.converter = self.context.as_converter()

    def expand(self, curie: str) -> str:
        pass
#        return self.converter.expand(curie)



