"""Tests for API settings that come from the environment."""

import importlib
import os
from unittest.mock import patch

import pytest
from loguru import logger

from monarch_py.api import config


@pytest.fixture(autouse=True)
def restore_config():
    """Reload the module afterwards either way.

    `log_level`'s default is evaluated at import, so these tests reload to see a
    different environment, and reload again on the way out so a failure does not leave
    the changed default in place for everything after it.
    """
    yield
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("MONARCH_LOG_LEVEL", None)
        importlib.reload(config)


def reload_with(value=None):
    with patch.dict(os.environ, {}, clear=False):
        if value is None:
            os.environ.pop("MONARCH_LOG_LEVEL", None)
        else:
            os.environ["MONARCH_LOG_LEVEL"] = value
        importlib.reload(config)
        return config.Settings().log_level


def test_defaults_to_info_not_debug():
    """Without an explicit level the API falls back to loguru's DEBUG sink."""
    assert reload_with() == "INFO"


@pytest.mark.parametrize(
    "value,expected",
    [("DEBUG", "DEBUG"), ("debug", "DEBUG"), (" warning ", "WARNING")],
)
def test_override_is_accepted_however_it_is_typed(value, expected):
    assert reload_with(value) == expected


@pytest.mark.parametrize("value", ["INFOO", "", "verbose"])
def test_an_unusable_level_falls_back_rather_than_crashing(value):
    """loguru raises on an unknown level name, and at import that kills every worker."""
    assert reload_with(value) == "INFO"


def test_importing_the_api_actually_sets_the_sink_level():
    """The setting existing is not the fix; the sink being at that level is.

    Without this, deleting the `set_log_level` call from `api/main.py` leaves every
    other test here passing.
    """
    reload_with()
    import monarch_py.api.main  # noqa: F401 - imported for its side effect

    levels = [h.levelno for h in logger._core.handlers.values()]
    assert levels, "no loguru sink configured"
    assert min(levels) == logger.level("INFO").no, f"sink levels were {levels}"
