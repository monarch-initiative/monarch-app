from monarch_py.service.curie_service import CurieService
import pytest


@pytest.mark.parametrize(
    ("curie", "expanded_curie_part"),
    [("FB:FBgn0000008", "http://identifiers.org/flybase/FBgn0000008"), # this is a little odd, fb vs. flybase, but both resolve
     ("FlyBase:FBgn0000008", "http://identifiers.org/fb/FBgn0000008"),
     ("MONDO:0005737", "http://purl.obolibrary.org/obo/MONDO_0005737"),
     ("OMIM:613647", "http://identifiers.org/mim/613647"),
     ("NCBIGene:1017", "https://identifiers.org/ncbigene/1017"),
     ("ZFIN:ZDB-GENE-980526-166", "https://identifiers.org/zfin/ZDB-GENE-980526-166"),
     ("MGI:1918910", "https://identifiers.org/MGI/1918910"),
     ("ENSEMBL:ENSG00000157764", "http://identifiers.org/ensembl/ENSG00000157764")]
)
def test_curie_expansion(curie, expanded_curie_part):
    cs = CurieService()
    expanded_curie = cs.expand(curie)
    assert expanded_curie_part in expanded_curie
