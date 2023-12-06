from monarch_py.service.curie_service import CurieService
import pytest


@pytest.mark.parametrize(
    ("curie", "expanded_curie_part"),
    [
        (
            "FB:FBgn0000008",
            "http://identifiers.org/flybase/FBgn0000008",
        ),  # this is a little odd, fb vs. flybase, but both resolve
        ("FlyBase:FBgn0000008", "http://identifiers.org/fb/FBgn0000008"),
        ("MONDO:0005737", "http://purl.obolibrary.org/obo/MONDO_0005737"),
        ("OMIM:613647", "http://identifiers.org/mim/613647"),
        ("NCBIGene:1017", "https://identifiers.org/ncbigene/1017"),
        ("ZFIN:ZDB-GENE-980526-166", "https://identifiers.org/zfin/ZDB-GENE-980526-166"),
        ("MGI:1918910", "https://identifiers.org/MGI/1918910"),
        ("ENSEMBL:ENSG00000157764", "http://identifiers.org/ensembl/ENSG00000157764"),
        ("HP:0000001", "http://purl.obolibrary.org/obo/HP_0000001"),
        ("UBERON:0000001", "http://purl.obolibrary.org/obo/UBERON_0000001"),
        ("GO:0000001", "http://purl.obolibrary.org/obo/GO_0000001"),
        ("CL:0000001", "http://purl.obolibrary.org/obo/CL_0000001"),
        ("WormBase:WBGene00000001", "http://identifiers.org/wb/WBGene00000001"),
        ("WB:WBGene00000001", "https://identifiers.org/wb/WBGene00000001"),
        ("SGD:S000000001", "https://identifiers.org/sgd/S000000001"),
        ("RGD:1", "https://identifiers.org/rgd/1"),
        ("HGNC:5", "http://identifiers.org/hgnc/5"),
    ],
)
def test_curie_expansion(curie, expanded_curie_part):
    cs = CurieService()
    expanded_curie = cs.expand(curie)
    print(f"expanded_curie: {expanded_curie}\nexpanded_curie_part: {expanded_curie_part}")
    assert expanded_curie_part in expanded_curie
