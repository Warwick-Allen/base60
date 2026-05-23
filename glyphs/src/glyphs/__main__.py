"""Console entry point for glyphs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from glyphs.display import configure_matplotlib, show_or_save
from glyphs.stroke import stroke

configure_matplotlib()
import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Glyphs plotting toolkit")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Plot a simple sine curve to verify matplotlib and numpy",
    )
    parser.add_argument(
        "--stroke",
        type=str,
        metavar="STYLE",
        help="Render stroke glyph STYLE (e.g. --stroke='60')",
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
    elif args.stroke is not None:
        if args.stroke == "base":
            x_min = -1/16
            x_max =  1/16
        else:
            x_min = 0
            x_max = 1/2
        n = int(2000 * (x_max - x_min))
        lim = 1/2
        x, y1, y2 = stroke(args.stroke, x_min, x_max, n)
        plt.fill_between(x, y1, y2, color="green")
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)
        show_or_save(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
