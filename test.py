from monarch_py.api.additional_models import SemsimSearchGroup, SemsimMultiCompareObject, SemsimMultiCompareRequest
from monarch_py.api.semsim import _compare, _search, _post_multicompare
from monarch_py.utils.format_utils import format_output, to_json, to_tsv, to_yaml

fixtures = {}
fixtures["phenotype-explorer-multi-compare"] = _post_multicompare(
            request=SemsimMultiCompareRequest(
                subjects=["MP:0010771", "MP:0002169"],
                object_sets=[
                    SemsimMultiCompareObject(
                        id="test1", label="Test1", phenotypes=["HP:0004325"]
                    ),
                    SemsimMultiCompareObject(
                        id="test2", label="Test2", phenotypes=["HP:0000093"]
                    ),
                ],
                metric="jaccard_similarity",
            )
        )

to_json(fixtures["phenotype-explorer-multi-compare"])