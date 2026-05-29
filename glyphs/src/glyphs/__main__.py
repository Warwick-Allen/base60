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
from glyphs.svg import glyph_to_svg, save_glyph_svg
import io
import sys

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
        action="append",
        dest="svg",
        metavar="PATH",
        help="Save exact SVG to PATH; use '-' for stdout; repeatable",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Hide axes and decorations; show only the glyph",
    )
    parser.add_argument(
        "--png",
        action="append",
        dest="png",
        metavar="PATH",
        help="Save PNG to PATH; use '-' for stdout; repeatable",
    )
    args = parser.parse_args()

    if args.scheme is not None:
        glyph = _build_glyph_from_args(args.scheme, args.digit, args.placements, args.force)

        png_paths = args.png or []
        svg_paths = args.svg or []

        # If no explicit outputs requested, preserve interactive/headless behaviour
        if not png_paths and not svg_paths:
            plot_glyph(glyph, clean=args.clean)
            show_or_save(None)
            return

        # Generate SVG outputs first (they're text-based)
        for p in svg_paths:
            if p == "-":
                # Write SVG to stdout
                sys.stdout.write(glyph_to_svg(glyph))
                sys.stdout.flush()
            else:
                save_glyph_svg(glyph, Path(p))

        # Generate PNG outputs using the Matplotlib figure
        if png_paths:
            import matplotlib.pyplot as plt

            ax = plot_glyph(glyph, clean=args.clean)
            fig = ax.figure
            for p in png_paths:
                if p == "-":
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                    buf.seek(0)
                    # Write raw bytes to stdout buffer
                    sys.stdout.buffer.write(buf.read())
                    sys.stdout.buffer.flush()
                else:
                    target = Path(p).expanduser().resolve()
                    target.parent.mkdir(parents=True, exist_ok=True)
                    fig.savefig(target, dpi=150, bbox_inches="tight")
                    plt.close(fig)
                    print(f"Wrote {target}")
            # Close the figure if not already closed
            try:
                plt.close(fig)
            except Exception:
                pass
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
