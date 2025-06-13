from monarch_py.service.curie_service import converter
import pytest


@pytest.mark.parametrize(
    ("curie", "expected"),
    [
        (
            "FB:FBgn0000008",
            "identifiers.org/flybase/FBgn0000008",
        ),  # this is a little odd, fb vs. flybase, but both resolve
        ("FlyBase:FBgn0000008", "identifiers.org/fb/FBgn0000008"),
        ("MONDO:0005737", "purl.obolibrary.org/obo/MONDO_0005737"),
        ("NCBIGene:1017", "identifiers.org/ncbigene/1017"),
        ("ZFIN:ZDB-GENE-980526-166", "identifiers.org/zfin/ZDB-GENE-980526-166"),
        ("MGI:1918910", "identifiers.org/MGI/1918910"),
        ("HP:0000001", "purl.obolibrary.org/obo/HP_0000001"),
        ("GO:0000001", "purl.obolibrary.org/obo/GO_0000001"),
        ("CL:0000001", "purl.obolibrary.org/obo/CL_0000001"),
        ("WB:WBGene00000001", "identifiers.org/wb/WBGene00000001"),
        ("SGD:S000000001", "identifiers.org/sgd/S000000001"),
        ("RGD:1", "identifiers.org/rgd/1"),
        ("HGNC:5", "identifiers.org/hgnc/5"),
        ### These prefixes are currently broken in the curie service
        ("ENSEMBL:ENSG00000157764", "identifiers.org/ensembl/ENSG00000157764"),
        ("OMIM:613647", "identifiers.org/mim/613647"),
        ("UBERON:0000001", "purl.obolibrary.org/obo/UBERON_0000001"),
        ("WormBase:WBGene00000001", "identifiers.org/wb/WBGene00000001"),
    ],
)
def test_curie_expansion(curie, expected):
    expanded_curie = converter.expand(curie)
    # print(expanded_curie, expected)
    assert expected in expanded_curie
