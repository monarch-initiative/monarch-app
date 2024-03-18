from urllib.parse import urlencode
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from monarch_py.utils.utils import escape
from pydantic import BaseModel, Field


class core(Enum):
    ENTITY = "entity"
    ASSOCIATION = "association"
    SSSOM = "sssom"


class HistoPhenoKeys(Enum):
    skeletal_system = "HP:0000924" # UPHENO:0002964"
    nervous_system = "HP:0000707" # UPHENO:0004523
    head_neck = "HP:0000152" # UPHENO:0002764
    integument = "HP:0001574" # UPHENO:0002635
    eye = "HP:0000478" #  UPHENO:0003020
    cardiovascular_system = "HP:0001626" # UPHENO:0080362
    metabolism_homeostasis = "HP:0001939" # ???
    genitourinary_system = "HP:0000119" # UPHENO:0002642
    digestive_system = "HP:0025031" # UPHENO:0002833
    neoplasm = "HP:0002664" # ???
    blood = "HP:0001871" # UPHENO:0004459
    immune_system = "HP:0002715" # UPHENO:0002948
    endocrine = "HP:0000818" # UPHENO:0003116
    musculature = "HP:0003011" # UPHENO:0002816
    respiratory = "HP:0002086" # UPHENO:0004536
    ear = "HP:0000598" # UPHENO:0002903
    connective_tissue = "HP:0003549" # UPHENO:0002712
    prenatal_or_birth = "HP:0001197" # UPHENO:0075949
    growth = "HP:0001507" # UPHENO:0049874
    breast = "HP:0000769" # UPHENO:0003013


class SolrQuery(BaseModel):
    q: str = "*:*"
    rows: int = 20
    start: int = 0
    facet: bool = True
    facet_min_count: int = 1
    facet_fields: Optional[List[str]] = Field(default_factory=list)
    facet_queries: Optional[List[str]] = Field(default_factory=list)
    filter_queries: Optional[List[str]] = Field(default_factory=list)
    query_fields: Optional[str] = None
    def_type: str = "edismax"
    q_op: str = "AND"  # See SOLR-8812, need this plus mm=100% to allow boolean operators in queries
    mm: str = "100%"  # All tokens in the query must be found in the doc
    boost: Optional[str] = None
    sort: Optional[str] = None

    def add_field_filter_query(self, field: str, value: Union[list, str, None]):
        if not value or len(value) == 0:
            return self
        if isinstance(value, list):
            fq = " OR ".join([f"{field}:{escape(val)}" for val in value])
        else:
            fq = f"{field}:{escape(value)}"
        self.filter_queries.append(fq)
        return self

    def add_filter_query(self, filter_query: Union[list, str, None]):
        if not filter_query:
            return self
        if isinstance(filter_query, list):
            filter_query = " OR ".join(escape(filter_query))
        self.filter_queries.append(filter_query)
        return self

    def query_string(self):
        return urlencode(
            {self._solrize(k): self._solrize(v) for k, v in self.model_dump().items() if v is not None},
            doseq=True,
        )

    def _solrize(self, value):
        """
        Rename fields and values as necessary to go from the python API to solr query syntax
        """
        if value == "facet_fields":
            return "facet.field"
        elif value == "facet_queries":
            return "facet.query"
        elif value == "filter_queries":
            return "fq"
        elif value == "query_fields":
            return "qf"
        elif value == "def_type":
            return "defType"
        elif value == "q_op":
            return "q.op"
        elif value is True:
            return "true"
        elif value is False:
            return "false"
        else:
            return value


class SolrQueryResponseHeader(BaseModel):
    QTime: int
    params: Any


class SolrQueryResponse(BaseModel):
    num_found: int = Field(alias="numFound")
    start: int
    docs: List[Any]


class SolrFacetCounts(BaseModel):
    facet_fields: Optional[Dict]
    facet_queries: Optional[Dict]


class SolrQueryResult(BaseModel):
    responseHeader: SolrQueryResponseHeader
    response: SolrQueryResponse
    facet_counts: Optional[SolrFacetCounts]
