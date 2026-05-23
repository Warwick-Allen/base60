"""Smoke tests for package metadata."""

import glyphs


def test_version_is_string() -> None:
    assert isinstance(glyphs.__version__, str)
    assert glyphs.__version__
