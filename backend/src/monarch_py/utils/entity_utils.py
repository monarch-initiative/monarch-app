import re
from monarch_py.datamodels.model import ExpandedCurie
from monarch_py.service.curie_service import converter

__all__ = [
    "get_expanded_curie",
]


def expansion_patch(url: str):
    """Any short term patches that we need while waiting for upstream fixes"""

    # This fixes MGI urls that take the form of
    # https://identifiers.org/MGI/97486
    # rather than https://identifiers.org/MGI:97486
    pattern = r"/MGI/(\d+)$"
    replacement = r"/MGI:\1"
    return re.sub(pattern, replacement, url)


def get_uri(id: str) -> str:
    """Returns the URI for the given CURIE."""
    return expansion_patch(converter.expand(id))


def get_expanded_curie(id: str) -> ExpandedCurie:
    """Returns the URI for the given CURIE."""
    return ExpandedCurie(id=id, url=converter.expand(id))
