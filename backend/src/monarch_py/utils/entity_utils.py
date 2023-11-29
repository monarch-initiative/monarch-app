from monarch_py.datamodels.model import ExpandedCurie
from monarch_py.service.curie_service import CurieService


def get_uri(id: str) -> str:
    """Returns the URI for the given CURIE."""
    return CurieService().expand(id)


def get_expanded_curie(id: str) -> ExpandedCurie:
    """Returns the URI for the given CURIE."""
    return ExpandedCurie(id=id, url=get_uri(id))
