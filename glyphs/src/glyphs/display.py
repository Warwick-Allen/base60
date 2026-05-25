"""Matplotlib display helpers for headless and WSL environments."""

from __future__ import annotations

import os
import warnings
from pathlib import Path

import matplotlib
from matplotlib.backends import backend_registry

_INTERACTIVE_BACKENDS = ("TkAgg", "Qt5Agg", "QtAgg", "GTK4Agg", "GTK3Agg", "WXAgg")
_NON_INTERACTIVE_BACKENDS = frozenset(
    {"agg", "pdf", "ps", "svg", "cairo", "template", "webagg"}
)


def configure_matplotlib() -> None:
    """Pick a GUI backend when a display is available, otherwise use Agg."""
    if os.environ.get("MPLBACKEND"):
        return

    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if not has_display:
        matplotlib.use("Agg", force=True)
        return

    for backend in _INTERACTIVE_BACKENDS:
        try:
            backend_registry.load_backend_module(backend)
        except (ImportError, ModuleNotFoundError, ValueError):
            continue
        matplotlib.use(backend, force=True)
        return

    matplotlib.use("Agg", force=True)


def backend_is_interactive() -> bool:
    return matplotlib.get_backend().lower() not in _NON_INTERACTIVE_BACKENDS


def show_or_save(
    output: Path | None = None,
    *,
    default_name: str = "glyphs.png",
) -> Path | None:
    """Show the current figure interactively, or save it when no GUI is available."""
    import matplotlib.pyplot as plt

    if output is not None:
        path = output.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Wrote {path}")
        return path

    if backend_is_interactive():
        plt.show()
        return None

    path = Path(default_name).resolve()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    warnings.warn(
        "No interactive matplotlib backend is available (common on WSL without "
        "python3-tk or Qt bindings). The plot was saved instead. Install a GUI "
        "backend, for example: sudo apt install python3-tk",
        stacklevel=2,
    )
    print(f"Wrote {path}")
    return path
