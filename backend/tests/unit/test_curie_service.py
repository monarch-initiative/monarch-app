from monarch_py.service.curie_service import CurieService
import pytest


@pytest.mark.parametrize(
    ("curie", "expanded_curie_part"),
    [("FB:FBgn0000008", "flybase.org"),
     ("FlyBase:FBgn0000008", "flybase.org")],
)
def test_curie_expansion(curie, expanded_curie_part):
    cs = CurieService()
    expanded_curie = cs.expand(curie)
    assert expanded_curie_part in expanded_curie
