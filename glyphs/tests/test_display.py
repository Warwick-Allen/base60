"""Tests for matplotlib display helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

from glyphs.display import backend_is_interactive, configure_matplotlib, show_or_save


@pytest.fixture(autouse=True)
def reset_backend() -> None:
    matplotlib.use("Agg", force=True)
    plt.switch_backend("Agg")
    yield
    plt.close("all")


def test_backend_is_interactive_for_agg() -> None:
    assert not backend_is_interactive()


def test_show_or_save_writes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    configure_matplotlib()

    plt.plot([0, 1], [0, 1])
    out = tmp_path / "plot.png"
    path = show_or_save(out)
    assert path == out.resolve()
    assert out.is_file()


def test_show_or_save_default_when_headless(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("MPLBACKEND", "Agg")
    configure_matplotlib()

    plt.plot([0, 1], [1, 0])
    with pytest.warns(UserWarning, match="No interactive matplotlib backend"):
        path = show_or_save()
    assert path is not None
    assert path.name == "glyphs-demo.png"
    assert path.is_file()
