"""Console entry point for gyphs."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Gyphs plotting toolkit")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Show a simple sine plot to verify matplotlib and numpy",
    )
    args = parser.parse_args()

    if args.demo:
        x = np.linspace(0, 2 * np.pi, 200)
        y = np.sin(x)
        plt.plot(x, y)
        plt.title("gyphs demo")
        plt.xlabel("x")
        plt.ylabel("sin(x)")
        plt.show()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
