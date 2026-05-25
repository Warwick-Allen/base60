"""Matplotlib rendering for glyphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from glyphs.glyph import Glyph
from glyphs.stroke import StrokeGeometry, glyph_strokes

if TYPE_CHECKING:
    from matplotlib.axes import Axes

OFFSET_X = 1/2
OFFSET_Y = 1/4
CANVAS_LIMIT_X = [-1/2 + OFFSET_X, 1/2 + OFFSET_X]
CANVAS_LIMIT_Y = [-1/2 + OFFSET_Y, 1/2 + OFFSET_Y]


def _fill_stroke(ax: Axes, geom: StrokeGeometry, *, color: str, alpha: float) -> None:
    verts = np.vstack(
        [
            np.column_stack([geom.x_upper, geom.y1]),
            np.column_stack([geom.x_lower[::-1], geom.y2[::-1]]),
        ]
    )
    xs = verts[:, 0] + OFFSET_X
    ys = verts[:, 1] + OFFSET_Y
    ax.fill(xs, ys, color=color, alpha=alpha)


def plot_glyph(
    glyph: Glyph,
    n: int = 1000,
    *,
    ax: Axes | None = None,
    stem_colour: str = "black",
    arm_colour: str = "black",
    arm_alpha: float = 1.0,
    clean: bool = False,
) -> Axes:
    """Draw a full glyph on the given axes (or create a new figure)."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()
    strokes = glyph_strokes(glyph, n)
    _fill_stroke(ax, strokes[0], color=stem_colour, alpha=1.0)
    for geom in strokes[1:]:
        _fill_stroke(ax, geom, color=arm_colour, alpha=arm_alpha)
    ax.set_xlim(*CANVAS_LIMIT_X)
    ax.set_ylim(*CANVAS_LIMIT_Y)
    ax.set_aspect("equal")
    if clean:
        # Hide axes decorations so only the glyph is visible
        ax.set_axis_off()
    return ax
