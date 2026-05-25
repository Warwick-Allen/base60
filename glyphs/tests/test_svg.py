"""Tests for exact SVG glyph export."""

from __future__ import annotations

from pathlib import Path

from glyphs.encoding import glyph_for_digit
from glyphs.scheme import Scheme
from glyphs.svg import glyph_to_svg, save_glyph_svg


def test_glyph_to_svg_includes_expected_elements() -> None:
    glyph = glyph_for_digit(Scheme.S60, 12)
    svg = glyph_to_svg(glyph)
    assert svg.startswith("<svg")
    assert "<defs>" in svg
    assert "path id=\"stem-60\"" in svg
    assert "path id=\"arm-60\"" in svg
    assert "use href=\"#stem-60\"" in svg
    assert "rotate(90)" in svg


def test_save_glyph_svg_writes_file(tmp_path: Path) -> None:
    glyph = glyph_for_digit(Scheme.S64, 0)
    output_file = tmp_path / "zero.svg"
    saved_path = save_glyph_svg(glyph, output_file)
    assert saved_path == output_file.resolve()
    content = output_file.read_text(encoding="utf-8")
    assert "<svg" in content
    assert "path id=\"stem-64\"" in content
