"""Console entry point for glyphs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from glyphs.display import configure_matplotlib, show_or_save

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
        type=int,
        metavar="N",
        help="Render stroke glyph N (e.g. --stroke=60)",
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
        k = 0.5
        n = 1000
        x = np.linspace(0, k, n)
        match args.stroke:
            case 60:
                y1 = (1 - (4*x - 1)**2)/4
                # log(2x) is undefined at x=0; limit of y2 is 0 there (y1=0, denom→∞)
                positive = x > 0
                y2 = np.zeros_like(x)
                y2[positive] = y1[positive]/(1 - np.log(2*x[positive]))
            case 64:
                y1 = (1 - abs(4*x - 1)**(1/2))/2
                y2 = y1*4/5
            case _:
                raise ValueError(f"Unknown stroke: {args.stroke}")
        plt.fill_between(x, y1, y2, color='green')
        plt.xlim(-k, k)
        plt.ylim(-k, k)
        show_or_save(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
