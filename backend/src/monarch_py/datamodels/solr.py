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
    skeletal_system = "UPHENO:0002964"  # "HP:0000924"
    nervous_system = "UPHENO:0004523"  # "HP:0000707"
    head_neck = "UPHENO:0002764"  # "HP:0000152"
    integument = "UPHENO:0002635"  # "HP:0001574"
    eye = "UPHENO:0003020"  # "HP:0000478"
    cardiovascular_system = "UPHENO:0080362"  # "HP:0001626"
    metabolism_homeostasis = "HP:0001939"  # ??? No uPheno parent
    genitourinary_system = "UPHENO:0002642"  # "HP:0000119"
    digestive_system = "UPHENO:0002833"  # "HP:0025031"
    neoplasm = "HP:0002664"  # ??? No uPheno parent
    blood = "UPHENO:0004459"  # "HP:0001871"
    immune_system = "UPHENO:0002948"  # "HP:0002715"
    endocrine = "UPHENO:0003116"  # "HP:0000818"
    musculature = "UPHENO:0002816"  # "HP:0003011"
    respiratory = "UPHENO:0004536"  # "HP:0002086"
    ear = "HP:0000598"  # UPHENO:0002903
    connective_tissue = "UPHENO:0002712"  # "HP:0003549"
    prenatal_or_birth = "UPHENO:0075949"  # "HP:0001197"
    growth = "UPHENO:0049874"  # "HP:0001507"
    breast = "UPHENO:0003013"  # "HP:0000769"


class SolrQuery(BaseModel):
    q: str = "*:*"
    rows: int = 20
    start: int = 0
    facet: bool = True
    facet_min_count: int = 1
    facet_fields: Optional[List[str]] = Field(default_factory=list)
    facet_queries: Optional[List[str]] = Field(default_factory=list)
    filter_queries: Optional[List[str]] = Field(default_factory=list)
    facet_mincount: int = 1
    query_fields: Optional[str] = None
    def_type: str = "edismax"
    q_op: str = "AND"  # See SOLR-8812, need this plus mm=100% to allow boolean operators in queries
    mm: str = "100%"  # All tokens in the query must be found in the doc
    boost: Optional[str] = None
    sort: Optional[str] = None
    hl: bool = False

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
        elif value == "facet_mincount":
            return "facet.mincount"
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
    highlighting: Optional[Dict[str, Dict[str, Optional[List[str]]]]] = Field(default_factory=dict)
