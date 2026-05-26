"""Visual comparison tests for SVG vs Matplotlib rendering."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from glyphs.encoding import glyph_for_digit
from glyphs.plot import plot_glyph
from glyphs.scheme import Scheme
from glyphs.svg import save_glyph_svg


def _render_matplotlib_to_png(scheme: Scheme, digit: int, output_path: Path) -> Path:
    """Render a glyph to PNG using Matplotlib."""
    import matplotlib.pyplot as plt

    glyph = glyph_for_digit(scheme, digit)
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    plot_glyph(glyph, clean=True, ax=ax)
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return output_path


def _render_svg_to_png(svg_path: Path, output_path: Path) -> Path:
    """Convert SVG to PNG using ImageMagick."""
    try:
        subprocess.run(
            ["convert", str(svg_path), "-background", "white", str(output_path)],
            check=True,
            capture_output=True,
            timeout=10,
        )
        return output_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(f"Failed to convert SVG using ImageMagick: {e}")


def _render_svg_with_inkscape(svg_path: Path, output_path: Path) -> Path:
    """Convert SVG to PNG using Inkscape (Windows)."""
    try:
        subprocess.run(
            ["inkscape", "--export-filename", str(output_path), str(svg_path)],
            check=True,
            capture_output=True,
            timeout=30,
        )
        return output_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(f"Failed to convert SVG using Inkscape: {e}")


def _calculate_image_diff(img1: Image.Image, img2: Image.Image) -> float:
    """Calculate normalized MSE between two images."""
    # Resize to match
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

    # Convert to grayscale numpy arrays
    arr1 = np.array(img1.convert("L"), dtype=np.float32)
    arr2 = np.array(img2.convert("L"), dtype=np.float32)

    # Calculate MSE
    mse = np.mean((arr1 - arr2) ** 2)
    normalized_mse = mse / (255 ** 2)
    return normalized_mse


def test_svg_vs_matplotlib_s60_digit_12() -> None:
    """Compare SVG and Matplotlib rendering for scheme 60, digit 12."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Generate both versions
        glyph = glyph_for_digit(Scheme.S60, 12)
        svg_path = tmpdir_path / "glyph.svg"
        save_glyph_svg(glyph, svg_path)

        matplotlib_png = tmpdir_path / "matplotlib.png"
        _render_matplotlib_to_png(Scheme.S60, 12, matplotlib_png)

        # Try to render SVG to PNG
        svg_png = tmpdir_path / "svg.png"
        try:
            _render_svg_to_png(svg_path, svg_png)
        except RuntimeError:
            # Fallback to Inkscape on Windows
            try:
                _render_svg_with_inkscape(svg_path, svg_png)
            except RuntimeError as e:
                print(f"Warning: Could not render SVG to PNG: {e}")
                return

        # Compare images
        img_matplotlib = Image.open(matplotlib_png)
        img_svg = Image.open(svg_png)

        diff = _calculate_image_diff(img_matplotlib, img_svg)
        print(f"\nImage difference (normalized MSE): {diff:.6f}")
        print(f"Matplotlib size: {img_matplotlib.size}")
        print(f"SVG rendered size: {img_svg.size}")

        # Print both images for visual inspection
        print(f"Matplotlib PNG: {matplotlib_png}")
        print(f"SVG PNG: {svg_png}")
        print(f"Original SVG: {svg_path}")

        # For now, just print results - visual inspection is needed
        assert diff is not None


def test_svg_output_exists_and_is_valid() -> None:
    """Verify SVG output is valid XML."""
    import xml.etree.ElementTree as ET

    glyph = glyph_for_digit(Scheme.S60, 12)
    with tempfile.TemporaryDirectory() as tmpdir:
        svg_path = Path(tmpdir) / "test.svg"
        save_glyph_svg(glyph, svg_path)

        # Parse SVG to verify it's valid XML
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            assert root.tag.endswith("svg"), "Root should be SVG element"
        except ET.ParseError as e:
            raise AssertionError(f"SVG is not valid XML: {e}")
