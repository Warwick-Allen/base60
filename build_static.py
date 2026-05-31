#!/usr/bin/env python3
"""build_static.py — Build a self-contained static index.html for GitHub Pages.

Reads static/index.html, pre-generates every SVG glyph and every Lembrent name
required by the page's JavaScript, and inlines them as a JSON data block.  The
resulting file is written to index.html in the repository root and requires no
API server to function.

Usage
-----
    python build_static.py [--source static/index.html] [--output index.html]

Requirements
------------
    pip install -e "glyphs/.[dev]"   # glyphs Python package (in this repo)
    Perl 5 must be on PATH           # for the lembrent name generator
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional pretty progress output
# ---------------------------------------------------------------------------
try:
    from math import ceil
    _TTY = sys.stderr.isatty()
except Exception:
    _TTY = False


def _progress(msg: str) -> None:
    print(f"  {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Repository layout
# ---------------------------------------------------------------------------
PROJECT_ROOT   = Path(__file__).resolve().parent
LEMBRENT_PATH  = PROJECT_ROOT / "lembrent" / "lembrent"
SOURCE_DEFAULT = PROJECT_ROOT / "static" / "index.html"
OUTPUT_DEFAULT = PROJECT_ROOT / "index.html"


# ---------------------------------------------------------------------------
# Lembrent name generation
# ---------------------------------------------------------------------------

def _lembrent_name(radix: int, number: int) -> str:
    """Return the Lembrent name for *number* in the given *radix* (60 or 64)."""
    result = subprocess.run(
        ["perl", str(LEMBRENT_PATH), str(radix), str(number)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"lembrent exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def generate_lembrent_names(sample_numbers: list[int]) -> dict[str, dict[str, str]]:
    """Pre-generate Lembrent names for every number needed by the static page.

    Returns a mapping  {radix_str: {number_str: name_str}}, e.g.
        {"60": {"0": "see", "70": "seen-eet-eben", …}, "64": {…}}
    """
    names: dict[str, dict[str, str]] = {"60": {}, "64": {}}

    # Digit names for the reference grid (0–63); used by digitNameFromAPI().
    all_digits = set(range(64))

    # Sample-table numbers
    sample_set = set(sample_numbers)

    # Calculator default inputs (from the HTML): "123 + 456 * 2" = 1035, and 70.
    # Include a broad common range so typical calculator entries work offline.
    common_values = set(range(2001)) | {1035, 70}

    all_numbers = all_digits | sample_set | common_values

    total = len(all_numbers) * 2
    done  = 0
    _progress(f"Generating Lembrent names for {len(all_numbers)} numbers × 2 bases …")

    for n in sorted(all_numbers):
        for radix in (60, 64):
            radix_key = str(radix)
            n_key      = str(n)
            if n_key not in names[radix_key]:
                names[radix_key][n_key] = _lembrent_name(radix, n)
            done += 1
        if done % 20 == 0 or done == total:
            _progress(f"  names: {done}/{total}")

    return names


# ---------------------------------------------------------------------------
# SVG generation
# ---------------------------------------------------------------------------

def generate_all_svgs() -> dict[str, dict[str, str]]:
    """Return SVG markup for every digit in both schemes.

    Returns  {"60": {"0": "<svg…>", …, "59": "…"}, "64": {"0": "…", …, "63": "…"}}
    """
    # Import here so the script fails clearly when the package is absent.
    from glyphs import (                                      # noqa: PLC0415
        glyph_for_digit,
        glyph_to_svg,
        Scheme,
    )

    svgs: dict[str, dict[str, str]] = {"60": {}, "64": {}}

    _progress("Generating SVG glyphs for Scheme-60 (digits 0–59) …")
    for digit in range(60):
        g = glyph_for_digit(Scheme.S60, digit)
        svgs["60"][str(digit)] = glyph_to_svg(g)

    _progress("Generating SVG glyphs for Scheme-64 (digits 0–63) …")
    for digit in range(64):
        g = glyph_for_digit(Scheme.S64, digit)
        svgs["64"][str(digit)] = glyph_to_svg(g)

    total_chars = sum(len(v) for d in svgs.values() for v in d.values())
    _progress(f"SVG generation complete ({total_chars:,} chars, ~{total_chars // 1024} KB)")

    return svgs


# ---------------------------------------------------------------------------
# Sample-number set (mirrors buildSampleSet() in the original JS)
# ---------------------------------------------------------------------------

def build_sample_numbers(limit: int = 90) -> list[int]:
    """Replicate the JS buildSampleSet() logic in Python."""
    import math
    nums: set[int] = set(range(64))

    for radix in (60, 64):
        for e in range(1, 6):
            p = radix ** e
            for d in range(-2, 3):
                n = math.floor(math.pow(p, math.pow(1.004, d)))
                if 0 <= n < 1_000_000_000:
                    nums.add(n)

    return sorted(nums)[:limit]


# ---------------------------------------------------------------------------
# JavaScript data block injector
# ---------------------------------------------------------------------------

_MARKER_START = "/* __STATIC_DATA_START__ */"
_MARKER_END   = "/* __STATIC_DATA_END__ */"

_SHIM_TEMPLATE = (
    "/* __STATIC_DATA_START__ */\n"
    "/* AUTO-GENERATED by build_static.py — do not edit by hand. */\n"
    "(function () {{\n"
    '  "use strict";\n'
    "\n"
    "  /* ── Pre-generated SVG glyphs ────────────────────────────────────────── */\n"
    "  var SVG_DATA = {svg_json};\n"
    "\n"
    "  /* ── Pre-generated Lembrent names ───────────────────────────────────── */\n"
    "  var NAME_DATA = {name_json};\n"
    "\n"
    "  /* ── Helpers ─────────────────────────────────────────────────────────── */\n"
    "\n"
    "  /**\n"
    "   * Convert a non-negative integer to its base-radix digits, most\n"
    "   * significant first (mirrors to_base_digits() in the API).\n"
    "   */\n"
    "  function toBaseDigits(number, radix) {{\n"
    "    if (number === 0) return [0];\n"
    "    var digits = [];\n"
    "    var n = Math.floor(number);\n"
    "    while (n > 0) {{\n"
    "      digits.unshift(n % radix);\n"
    "      n = Math.floor(n / radix);\n"
    "    }}\n"
    "    return digits;\n"
    "  }}\n"
    "\n"
    "  /**\n"
    "   * Intercept every call to the live API and return pre-generated data\n"
    "   * instead.  The response shape is identical to the real API so that all\n"
    "   * downstream JS code is unmodified.\n"
    "   */\n"
    "  window.fetchLembrent = async function fetchLembrent(radix, number) {{\n"
    "    var radixKey  = String(radix);\n"
    "    var numberKey = String(number);\n"
    "    var nameStore = NAME_DATA[radixKey];\n"
    "    var svgStore  = SVG_DATA[radixKey];\n"
    "\n"
    "    if (!nameStore || !svgStore) return null;\n"
    "\n"
    "    var name = nameStore[numberKey];\n"
    "    if (name === undefined) return null;   // number not pre-generated\n"
    "\n"
    "    var digits = toBaseDigits(number, radix);\n"
    "    var svgList = [];\n"
    "    for (var i = 0; i < digits.length; i++) {{\n"
    "      var s = svgStore[String(digits[i])];\n"
    "      if (s) svgList.push(s);\n"
    "    }}\n"
    "\n"
    "    return {{ name: name, svg: svgList }};\n"
    "  }};\n"
    "\n"
    "  /* ── API live-query stub ─────────────────────────────────────────────── */\n"
    "  /*\n"
    "   * The 'API live query' panel posts to /lembrent/...  When served\n"
    "   * statically there is no server, so we patch fetch() for that panel to\n"
    "   * use the pre-generated data and format the response as pretty-printed\n"
    "   * JSON (matching what the panel expects).\n"
    "   */\n"
    "  var _realFetch = window.fetch.bind(window);\n"
    "  window.fetch = async function patchedFetch(url, opts) {{\n"
    r"    if (typeof url === 'string' && /^\/lembrent\//.test(url)) {{" + "\n"
    r"      var parts   = url.replace(/\?.*$/, '').split('/');" + "   // ['', 'lembrent', radix, number]\n"
    "      var radix60  = parseInt(parts[2], 10);\n"
    "      var num      = parseInt(parts[3], 10);\n"
    "      var radixKey = String(radix60);\n"
    "      var numKey   = String(num);\n"
    "      var nameVal  = (NAME_DATA[radixKey] || {{}})[numKey] || '\u2014';\n"
    "      var digits   = toBaseDigits(num, radix60);\n"
    "      var svgStore = SVG_DATA[radixKey] || {{}};\n"
    "      var svgList  = digits.map(function (d) {{ return svgStore[String(d)] || ''; }});\n"
    "      var body     = JSON.stringify({{ name: nameVal, svg: svgList }}, null, 2);\n"
    "      return new Response(body, {{\n"
    "        status:  200,\n"
    "        headers: {{ 'Content-Type': 'application/json' }},\n"
    "      }});\n"
    "    }}\n"
    "    return _realFetch(url, opts);\n"
    "  }};\n"
    "}})();\n"
    "/* __STATIC_DATA_END__ */"
)


def inject_data_block(html: str, svgs: dict, names: dict) -> str:
    """Insert (or replace) the pre-generated data shim into the HTML source."""
    # Compact JSON — readable but not bloated
    svg_json  = json.dumps(svgs,  separators=(", ", ": "), ensure_ascii=False)
    name_json = json.dumps(names, separators=(", ", ": "), ensure_ascii=False)

    shim = _SHIM_TEMPLATE.format(svg_json=svg_json, name_json=name_json)

    # Remove any previous shim block
    if _MARKER_START in html:
        start = html.index(_MARKER_START)
        end   = html.index(_MARKER_END) + len(_MARKER_END)
        html  = html[:start] + html[end:]

    # Insert the shim immediately after the opening <script> tag of the main
    # script block (the last one in the file, which contains the page logic).
    insert_after = html.rfind("<script>")
    if insert_after == -1:
        # Fallback: prepend to </body>
        html = html.replace("</body>", f"<script>\n{shim}\n</script>\n</body>", 1)
    else:
        insert_pos = insert_after + len("<script>")
        html = html[:insert_pos] + "\n" + shim + "\n" + html[insert_pos:]

    return html


def add_static_notice(html: str) -> str:
    """Replace the spinner placeholders with a short static-mode notice."""
    notice = (
        '<span style="font-family:var(--f-mono);font-size:.85rem;color:var(--accent);">'
        "Static build — calculator and samples are pre-loaded."
        "</span>"
    )
    # Replace the two loading spinners that never resolve without a live API.
    html = html.replace(
        '<span class="spinner"></span> Loading glyphs…',
        notice,
        1,
    )
    html = html.replace(
        '<span class="spinner"></span> Loading samples…',
        notice,
        1,
    )
    return html


def patch_api_panel(html: str) -> str:
    """Adjust the API live-query panel label to clarify static-mode behaviour."""
    old = "<h3>Live Query</h3>\n    <p>Try the API directly from this page:</p>"
    new = (
        "<h3>Live Query</h3>\n"
        '    <p>Results are served from pre-generated data embedded in this page.</p>'
    )
    return html.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build a self-contained static index.html for GitHub Pages."
    )
    p.add_argument(
        "--source", "-s",
        type=Path,
        default=SOURCE_DEFAULT,
        help=f"Source HTML file (default: {SOURCE_DEFAULT.relative_to(PROJECT_ROOT)})",
    )
    p.add_argument(
        "--output", "-o",
        type=Path,
        default=OUTPUT_DEFAULT,
        help=f"Output HTML file (default: {OUTPUT_DEFAULT.relative_to(PROJECT_ROOT)})",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    source: Path = args.source.resolve()
    output: Path = args.output.resolve()

    print(f"build_static.py", file=sys.stderr)
    print(f"  source : {source}", file=sys.stderr)
    print(f"  output : {output}", file=sys.stderr)

    # --- Validation ----------------------------------------------------------
    if not source.exists():
        sys.exit(f"Error: source file not found: {source}")
    if not LEMBRENT_PATH.exists():
        sys.exit(f"Error: lembrent script not found: {LEMBRENT_PATH}")

    try:
        import glyphs  # noqa: F401
    except ImportError:
        sys.exit(
            "Error: the 'glyphs' Python package is not installed.\n"
            "Run:  pip install -e \"glyphs/.[dev]\""
        )

    # --- Data generation -----------------------------------------------------
    print("", file=sys.stderr)
    _progress("Step 1/3 — Generating SVG glyphs …")
    svgs = generate_all_svgs()

    print("", file=sys.stderr)
    _progress("Step 2/3 — Generating Lembrent names …")
    sample_numbers = build_sample_numbers()
    names = generate_lembrent_names(sample_numbers)

    # --- HTML manipulation ---------------------------------------------------
    print("", file=sys.stderr)
    _progress("Step 3/3 — Patching HTML …")

    html = source.read_text(encoding="utf-8")
    html = inject_data_block(html, svgs, names)
    html = add_static_notice(html)
    html = patch_api_panel(html)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    size_kb = output.stat().st_size // 1024
    print("", file=sys.stderr)
    _progress(f"Written: {output}  ({size_kb} KB)")
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
