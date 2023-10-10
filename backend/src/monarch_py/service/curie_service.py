### make a singleton class that uses prefixmap and curies to expand curies

import curies
from curies import Converter
import requests
import csv


def from_csv_url(url):
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if there's a download error

    csv_data = response.content.decode('utf-8').splitlines()
    csv_reader = csv.DictReader(csv_data)

    prefix_map = []
    for row in csv_reader:
        # Assuming the CSV columns match the desired dictionary keys
        # Adjust as needed if the CSV column names are different
        entry = {
            "prefix": row[1],
            "uri_prefix": row[2],
            "prefix_synonyms": [],
            "uri_prefix_synonyms": []
        }
        prefix_map.append(entry)

    return prefix_map


class CurieService:
    _instance = None
    converter: Converter

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurieService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        url = (
            "https://raw.githubusercontent.com/linkml/prefixmaps/main/src/prefixmaps/data/merged.csv"
        )

        self.converter = Converter.from_extended_prefix_map(from_csv_url(url))

    def expand(self, curie: str) -> str:
        return self.converter.expand(curie)
