"""Numbering schemes for glyph characters."""

from __future__ import annotations

from enum import Enum


class Scheme(Enum):
    """Base-60 or base-64 glyph scheme (strokes are never mixed)."""

    S60 = "60"
    S64 = "64"

    def max_digit(self) -> int:
        return 59 if self is Scheme.S60 else 63

    @classmethod
    def parse(cls, value: str) -> Scheme:
        match value.strip():
            case "60":
                return Scheme.S60
            case "64":
                return Scheme.S64
            case _:
                raise ValueError(f"Unknown scheme: {value!r}")
