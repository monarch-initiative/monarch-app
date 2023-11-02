from monarch_py.service.curie_service import CurieService


def get_uri(id: str) -> str:
    """Returns the URI for the given CURIE."""
    return CurieService().expand(id)
