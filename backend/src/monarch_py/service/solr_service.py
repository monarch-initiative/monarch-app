import json
from typing import Dict, List

import requests
from loguru import logger
from monarch_py.datamodels.solr import SolrGroupedQueryResult, SolrQuery, SolrQueryResult, core
from monarch_py.utils.utils import escape
from pydantic import BaseModel


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

    def group_query(self, q: SolrQuery) -> SolrGroupedQueryResult:
        url = f"{self.base_url}/{self.core.value}/select?{q.query_string()}"
        response = requests.get(url)
        logger.debug(f"SolrService.query: {url}")
        data = json.loads(response.text)
        if "error" in data:
            logger.error("Solr error message: " + data["error"]["msg"])
        response.raise_for_status()
        solr_query_result = SolrGroupedQueryResult.model_validate(data, from_attributes=True)
        for group in solr_query_result.grouped.values():
            for doc in group.doclist.docs:
                self._strip_json(
                    doc,
                    "_version_",
                    "iri",
                    "frequency_computed_sortable_float",
                    "has_quotient_sortable_float",
                    "has_percentage_sortable_float",
                )

        return solr_query_result

    def query(self, q: SolrQuery) -> SolrQueryResult:
        url = f"{self.base_url}/{self.core.value}/select?{q.query_string()}"
        response = requests.get(url)
        logger.debug(f"SolrService.query: {url}")
        data = json.loads(response.text)
        if "error" in data:
            logger.error("Solr error message: " + data["error"]["msg"])
        response.raise_for_status()
        solr_query_result = SolrQueryResult.model_validate(data, from_attributes=True)
        for doc in solr_query_result.response.docs:
            self._strip_json(
                doc,
                "_version_",
                "iri",
                "frequency_computed_sortable_float",
                "has_quotient_sortable_float",
                "has_percentage_sortable_float",
            )

        return solr_query_result

    def _strip_json(self, doc: dict, *fields_to_remove: str):
        for field in fields_to_remove:
            try:
                del doc[field]
            except KeyError:
                pass
        return doc

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
