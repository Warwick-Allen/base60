"""Console entry point for glyphs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from glyphs.display import configure_matplotlib, show_or_save
from glyphs.encoding import glyph_for_digit
from glyphs.glyph import Glyph
from glyphs.placement import Placement
from glyphs.plot import plot_glyph
from glyphs.scheme import Scheme
from glyphs.svg import save_glyph_svg

configure_matplotlib()
import matplotlib.pyplot as plt  # noqa: E402


def _parse_scheme(value: str) -> Scheme:
    return Scheme.parse(value)


def _build_glyph_from_args(
    scheme: Scheme, digit: int | None, placements: list[str] | None, force: bool = False
) -> Glyph:
    if digit is not None and placements:
        raise SystemExit("Use either --digit or --placement, not both")
    if digit is not None:
        return glyph_for_digit(scheme, digit, force=force)
    if placements:
        arms = frozenset(Placement.parse(t) for t in placements)
        return Glyph(scheme, arms)
    raise SystemExit("Specify --digit N or one or more --placement tokens")


def main() -> None:
    parser = argparse.ArgumentParser(description="Glyphs plotting toolkit")
    parser.add_argument(
        "--scheme",
        type=_parse_scheme,
        metavar="{60,64}",
        help="Numbering scheme: 60 or 64",
    )
    parser.add_argument(
        "--digit",
        type=int,
        metavar="N",
        help="Render glyph for digit N using bitmap encoding",
    )
    parser.add_argument(
        "--placement",
        action="append",
        dest="placements",
        metavar="TOKEN",
        help="Arm placement token (180+, 180-, 90+, 90-, 0+, 0-); repeatable",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow digits 60-63 in base-60 scheme (normally restricted to 0-59)",
    )
    parser.add_argument(
        "--svg",
        action="store_true",
        help="Export the glyph as an exact SVG image instead of raster output",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Hide axes and decorations; show only the glyph",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="PATH",
        help="Save the figure to PATH instead of opening a window",
    )
    args = parser.parse_args()

    if args.scheme is not None:
        glyph = _build_glyph_from_args(args.scheme, args.digit, args.placements, args.force)
        use_svg = args.svg or (args.output is not None and args.output.suffix.lower() == ".svg")
        if use_svg:
            output = args.output or Path("glyph.svg")
            save_glyph_svg(glyph, output)
        else:
            plot_glyph(glyph, clean=args.clean)
            show_or_save(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
