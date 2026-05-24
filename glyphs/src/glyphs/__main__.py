"""Console entry point for glyphs."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np

from glyphs.display import configure_matplotlib, show_or_save
from glyphs.encoding import glyph_for_digit
from glyphs.glyph import Glyph
from glyphs.placement import Placement
from glyphs.plot import plot_glyph
from glyphs.scheme import Scheme
from glyphs.stroke import stroke

configure_matplotlib()
import matplotlib.pyplot as plt  # noqa: E402


def _parse_scheme(value: str) -> Scheme:
    return Scheme.parse(value)


def _build_glyph_from_args(
    scheme: Scheme, digit: int | None, placements: list[str] | None
) -> Glyph:
    if digit is not None and placements:
        raise SystemExit("Use either --digit or --placement, not both")
    if digit is not None:
        return glyph_for_digit(scheme, digit)
    if placements:
        arms = frozenset(Placement.parse(t) for t in placements)
        return Glyph(scheme, arms)
    raise SystemExit("Specify --digit N or one or more --placement tokens")


def main() -> None:
    parser = argparse.ArgumentParser(description="Glyphs plotting toolkit")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Plot a simple sine curve to verify matplotlib and numpy",
    )
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
        "--stroke",
        type=str,
        metavar="STYLE",
        help="(Deprecated) Render a single legacy stroke style",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="PATH",
        help="Save the figure to PATH instead of opening a window",
    )
    args = parser.parse_args()

    if args.demo:
        x = np.linspace(0, 2 * np.pi, 200)
        y = np.sin(x)
        plt.plot(x, y)
        plt.title("glyphs demo")
        plt.xlabel("x")
        plt.ylabel("sin(x)")
        show_or_save(args.output)
    elif args.scheme is not None:
        glyph = _build_glyph_from_args(args.scheme, args.digit, args.placements)
        plot_glyph(glyph)
        show_or_save(args.output)
    elif args.stroke is not None:
        warnings.warn(
            "--stroke is deprecated; use --scheme with --digit or --placement",
            DeprecationWarning,
            stacklevel=1,
        )
        n = 1000
        x, y1, y2 = stroke(args.stroke, n)
        plt.fill_between(x, y1, y2, color="green")
        lim = 0.5
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)
        plt.gca().set_aspect("equal")
        show_or_save(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
