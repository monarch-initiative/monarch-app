import json
from typing import Dict, List

import requests
from loguru import logger
from monarch_py.datamodels.solr import SolrQuery, SolrQueryResult, core
from monarch_py.utils.utils import escape
from pydantic import BaseModel

FIELD_TYPE_SUFFIXES = ["_t", "_ac", "_grounding", "_sortable_float"]


class SolrService(BaseModel):
    base_url: str
    core: core

    def get(self, id):
        url = f"{self.base_url}/{self.core.value}/get?id={id}"
        response = requests.get(url)
        response.raise_for_status()
        entity = response.json()["doc"]
        try:
            self._strip_json(entity, "_version_", "iri")
        except TypeError:  # if entity is None
            return None
        return entity

    def query(self, q: SolrQuery) -> SolrQueryResult:
        url = f"{self.base_url}/{self.core.value}/select?{q.query_string()}"
        response = requests.get(url)
        logger.debug(f"SolrService.query: {url}")
        data = json.loads(response.text)
        if "error" in data:
            logger.error("Solr error message: " + data["error"]["msg"])
        response.raise_for_status()
        solr_query_result = SolrQueryResult.model_validate(data, from_attributes=True)
        solr_query_result.highlighting = SolrService._consolidate_highlights(
            solr_query_result.highlighting, FIELD_TYPE_SUFFIXES
        )
        for doc in solr_query_result.response.docs:
            SolrService._strip_excluded_fields(doc)
            doc["highlighting"] = solr_query_result.highlighting.get(doc["id"], [])

        return solr_query_result

    @staticmethod
    def _strip_excluded_fields(doc: dict):
        SolrService._strip_json(
            doc,
            "_version_",
            "iri",
            "frequency_computed_sortable_float",
            "has_quotient_sortable_float",
            "has_percentage_sortable_float",
        )
        SolrService._strip_json_by_suffix(doc, *FIELD_TYPE_SUFFIXES)

    @staticmethod
    def _strip_json(doc: dict, *fields_to_remove: str):
        for field in fields_to_remove:
            try:
                del doc[field]
            except KeyError:
                pass
        return doc

    @staticmethod
    def _strip_json_by_suffix(doc: dict, *suffixes_to_remove: str):
        for suffix in suffixes_to_remove:
            for key in list(doc.keys()):
                if key.endswith(suffix):
                    del doc[key]

    @staticmethod
    def _consolidate_highlights(
        highlights: Dict[str, Dict[str, List[str]]], suffixes: List[str]
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        For each field that's returned, collapse specified suffix highlighting down to the root field. For example, each
        highlight for name_t and name_ac should be merged into a unique list for name and the specified suffix fields should
        be removed from the highlights.
        """
        consolidated_highlights = highlights.copy()
        for id, highlight in consolidated_highlights.items():
            for field in list(highlight.keys()):
                for suffix in suffixes:
                    if field.endswith(suffix):
                        root_field = field[: -len(suffix)]
                        if root_field not in highlight:
                            highlight[root_field] = highlight[field]
                        else:
                            highlight[root_field] = list(set(highlight[root_field] + highlight[field]))
                            highlight[root_field].sort()
                        del highlight[field]

        return consolidated_highlights

    # Solr returns facet values and counts as a list, they make much more
    # sense as a dictionary
    def _facets_to_dict(self, facet_list: List[str]) -> Dict:
        return dict(zip(facet_list[::2], facet_list[1::2]))

    def get_filtered_facet(self, id, filter_field, facet_field):
        query = SolrQuery(
            rows=0,
            facet=True,
            facet_fields=[facet_field],
            filter_queries=[f"{filter_field}:{escape(id)}"],
        )

        result = self.query(query)

        facet_fields = result.facet_counts.facet_fields[facet_field]

        return self._facets_to_dict(facet_fields)
