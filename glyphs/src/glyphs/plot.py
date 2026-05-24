"""Matplotlib rendering for glyphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from glyphs.glyph import Glyph
from glyphs.stroke import StrokeGeometry, glyph_strokes

if TYPE_CHECKING:
    from matplotlib.axes import Axes

CANVAS_LIMIT = 0.5


def _fill_stroke(ax: Axes, geom: StrokeGeometry, *, color: str, alpha: float) -> None:
    verts = np.vstack(
        [
            np.column_stack([geom.x_upper, geom.y1]),
            np.column_stack([geom.x_lower[::-1], geom.y2[::-1]]),
        ]
    )
    ax.fill(verts[:, 0], verts[:, 1], color=color, alpha=alpha)


def plot_glyph(
    glyph: Glyph,
    n: int = 1000,
    *,
    ax: Axes | None = None,
    base_colour: str = "black",
    arm_colour: str = "black",
    arm_alpha: float = 1.0,
) -> Axes:
    """Draw a full glyph on the given axes (or create a new figure)."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()
    strokes = glyph_strokes(glyph, n)
    _fill_stroke(ax, strokes[0], color=base_colour, alpha=1.0)
    for geom in strokes[1:]:
        _fill_stroke(ax, geom, color=arm_colour, alpha=arm_alpha)
    ax.set_xlim(-CANVAS_LIMIT, CANVAS_LIMIT)
    ax.set_ylim(-CANVAS_LIMIT, CANVAS_LIMIT)
    ax.set_aspect("equal")
    return ax
