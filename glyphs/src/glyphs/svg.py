"""Exact SVG export for glyphs using analytic cubic stroke formulas."""

from __future__ import annotations

import math
from pathlib import Path
from textwrap import dedent
import sys

from glyphs.glyph import Glyph
from glyphs.placement import Placement
from glyphs.scheme import Scheme
from glyphs.stroke import arm_svg_path_data, stem_svg_path_data

_CANVAS_OFFSET_X = 0.5
_CANVAS_OFFSET_Y = 0.25


def glyph_to_svg(glyph: Glyph, size: int = 400) -> str:
    """Return exact SVG markup for a glyph.
    
    Args:
        glyph: The glyph to render
        size: Output size in pixels (width and height, default 400)
    """
    stem_id = f"stem-{glyph.scheme.value}"
    arm_id = f"arm-{glyph.scheme.value}"

    path_defs = "".join(
        [
            f'<path id="{stem_id}" d="{stem_svg_path_data(glyph.scheme)}"/>',
            f'<path id="{arm_id}" d="{arm_svg_path_data(glyph.scheme)}"/>',
        ]
    )
    uses = [f'<use href="#{stem_id}" fill="black"/>']
    for placement in sorted(glyph.arms, key=lambda p: p.bit_index):
        angle = math.degrees(placement.rotation_angle())
        transform = f"rotate({angle:.6g})"
        if placement.sign() < 0:
            transform = f"scale(-1,1) {transform}"
        uses.append(
            f'<use href="#{arm_id}" fill="black" transform="{transform}"/>'
        )

    return dedent(
        f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-_CANVAS_OFFSET_Y} 1 1" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet">
          <defs>
            {path_defs}
          </defs>
          <g transform="translate({_CANVAS_OFFSET_X},{_CANVAS_OFFSET_Y}) scale(1,-1)">
            {' '.join(uses)}
          </g>
        </svg>
        """
    ).strip()


def save_glyph_svg(glyph: Glyph, path: Path | str) -> Path | None:
    """Write exact SVG for a glyph to disk or stdout.

    If `path` is the string `"-"`, the SVG markup is written to standard
    output and `None` is returned. Otherwise the file is written and the
    resolved `Path` is returned.
    """
    svg_text = glyph_to_svg(glyph)
    if isinstance(path, str) and path == "-":
        sys.stdout.write(svg_text)
        sys.stdout.flush()
        return None

    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg_text, encoding="utf-8")
    print(f"Wrote {target}")
    return target
