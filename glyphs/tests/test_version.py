"""Smoke tests for package metadata."""

import gyphs


def test_version_is_string() -> None:
    assert isinstance(gyphs.__version__, str)
    assert gyphs.__version__
