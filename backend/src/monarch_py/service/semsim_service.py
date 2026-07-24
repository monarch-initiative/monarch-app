from typing import List, Any
import requests

from pydantic import BaseModel

from monarch_py.api.additional_models import SemsimMetric, SemsimMultiCompareRequest, SemsimDirectionality
from monarch_py.datamodels.model import TermSetPairwiseSimilarity, SemsimSearchResult, Entity


class SemsimianService(BaseModel):
    """A class that makes HTTP requests to the semsimian_server."""

    semsim_server_port: int
    semsim_server_host: str
    entity_implementation: Any  # TODO: should be EntityInterface

    def convert_tsps_data(self, data):
        """Convert to a format that can be coerced into a TermSetPairwiseSimilarity model

        TODO: currently, the response returned from semsimian_server doesn't
        100% match the TermSetPairwiseSimilarity model, so we perform some
        transformations below. once it does, we can remove all the code below
        and just return TermSetPairwiseSimilarity(**data)
        """
        # remove these similarity maps and fold them into the _best_matches dicts
        object_best_matches_similarity_map = self._convert_nans(data.pop("object_best_matches_similarity_map"))
        subject_best_matches_similarity_map = self._convert_nans(data.pop("subject_best_matches_similarity_map"))
        converted_data = {
            **data,
            **{
                # flatten the nested termset dicts
                "subject_termset": {k: v for d in data["subject_termset"] for k, v in d.items()},
                "object_termset": {k: v for d in data["object_termset"] for k, v in d.items()},
                "subject_best_matches": {
                    k: {**v, "similarity": subject_best_matches_similarity_map[k]}
                    for k, v in data["subject_best_matches"].items()
                },
                "object_best_matches": {
                    k: {**v, "similarity": object_best_matches_similarity_map[k]}
                    for k, v in data["object_best_matches"].items()
                },
            },
        }
        return converted_data

    def compare(
        self, subjects: List[str], objects: List[str], metric: SemsimMetric = SemsimMetric.ANCESTOR_INFORMATION_CONTENT
    ) -> TermSetPairwiseSimilarity:
        host = f"http://{self.semsim_server_host}:{self.semsim_server_port}"
        path = f"compare/{','.join(subjects)}/{','.join(objects)}/{metric}"
        url = f"{host}/{path}"

        print(f"Fetching {url}...")
        response = requests.get(url=url)
        data = response.json()
        results = self.convert_tsps_data(data)
        return TermSetPairwiseSimilarity(**results)

    def multi_compare(self, request: SemsimMultiCompareRequest) -> List[SemsimSearchResult]:
        comparison_results = [
            self.compare(request.subjects, object_set.phenotypes, request.metric) for object_set in request.object_sets
        ]
        results = [
            SemsimSearchResult(
                subject=Entity(id=object_set.id, name=object_set.label),
                score=comparison_result.average_score,
                similarity=comparison_result,
            )
            for object_set, comparison_result in zip(request.object_sets, comparison_results)
        ]
        return results

    def search(
        self,
        termset: List[str],
        prefix: str = None,
        metric: SemsimMetric = SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
        directionality: SemsimDirectionality = SemsimDirectionality.BIDIRECTIONAL,
        limit: int = 10,
        categories: List[str] = None,
        taxa: List[str] = None,
        prefixes: List[str] = None,
    ) -> List[SemsimSearchResult]:
        """The semsimian HTTP server indexes entities by a single CURIE prefix, so it can honor
        only the prefix form of a filter.

        When `prefix` is set the call is a legacy group search and any accompanying
        category/taxon arguments merely restate what the prefix already encodes, so they are
        redundant and ignored. When it is not, the caller has asked for something explicit that
        this backend cannot express — anything but a single prefix is refused rather than
        answered with a broader result set that looks filtered but is not.
        """
        if prefix is None:
            if categories or taxa or (prefixes and len(prefixes) > 1):
                raise NotImplementedError(
                    "the semsimian backend cannot filter by category or taxon, or across multiple "
                    "prefixes; use the ducksim backend (SEMSIM_BACKEND=ducksim or ?engine=ducksim)"
                )
            if not prefixes:
                raise ValueError("semsimian search requires a prefix")
            prefix = prefixes[0]
        host = f"http://{self.semsim_server_host}:{self.semsim_server_port}"
        path = f"search/{','.join(termset)}/{prefix}:/{metric}?limit={limit}&directionality={directionality.value} "
        url = f"{host}/{path}"

        print(f"Fetching {url}...")
        response = requests.get(url=url)
        data = response.json()
        results = [
            SemsimSearchResult(
                subject=self.entity_implementation.get_entity(i[2], extra=False),
                score=i[0],
                similarity=self.convert_tsps_data(i[1]),
            )
            for i in data
        ]

        return results

    @staticmethod
    def _convert_nans(input_dict, to_value=None):
        """
        Given an input dict of the form {<term>: {<field>: <value>, ...}}
        converts any <value> of 'NaN' to None.
        """
        for k, v in input_dict.items():
            for ik, iv in v.items():
                if iv == "NaN":
                    input_dict[k][ik] = None

        return input_dict
