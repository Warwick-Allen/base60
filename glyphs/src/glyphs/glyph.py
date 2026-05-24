"""Composable glyph: base stroke plus arm placements."""

from __future__ import annotations

from dataclasses import dataclass

from glyphs.placement import Placement
from glyphs.scheme import Scheme


@dataclass(frozen=True)
class Glyph:
    """A single character: one scheme, base stroke, and zero to six arms."""

    scheme: Scheme
    arms: frozenset[Placement]

    def __post_init__(self) -> None:
        if len(self.arms) > 6:
            raise ValueError(f"at most six arm strokes allowed, got {len(self.arms)}")
