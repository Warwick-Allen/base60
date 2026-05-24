# glyphs

Python toolkit for **base-60** and **base-64** glyph characters, built on [NumPy](https://numpy.org/) and [Matplotlib](https://matplotlib.org/).

Each character is a **base stroke** plus zero to six **arm strokes** in one scheme (`60` or `64`). Arms are encoded as a **6-bit bitmap** (digits `0`–`59` for scheme 60, `0`–`63` for scheme 64).

## Requirements

- Python 3.10+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Coordinate frame

- Canvas: `(-0.5, -0.5)` to `(0.5, 0.5)`
- Base tip at `(0, 0)`
- Canonical arm (before rotation) runs from the base toward `(0.5, 0)`

## Bitmap encoding (arm bits)

| Bit     | Sign | Rotation | Tip              |
|---------|------|----------|------------------|
| 0 (LSB) | `+`  | `π`      | `(-0.5, 0)` left |
| 1       | `-`  | `π`      | `(-0.5, 0)`      |
| 2       | `+`  | `π/2`    | `(0, 0.5)` above |
| 3       | `-`  | `π/2`    | `(0, 0.5)`       |
| 4       | `+`  | `0`      | `(0.5, 0)` right |
| 5 (MSB) | `-`  | `0`      | `(0.5, 0)`       |

Digit **12** = bits 2 and 3 set (`π/2` + and `π/2` −):

```
 ( )
  |
```

Scheme **60** forbids digits **60–63** (invalid in base 60).

## Usage

Render a digit (scheme 60, digit 12):

```bash
glyphs --scheme 60 --digit 12 -o twelve.png
```

Base only (digit 0):

```bash
glyphs --scheme 64 --digit 0 -o zero.png
```

Manual arms:

```bash
glyphs --scheme 60 --placement 90+ --placement 90- -o manual.png
```

Placement tokens: `180+`, `180-`, `90+`, `90-`, `0+`, `0-`.

### Python API

```python
from glyphs import Scheme, glyph_for_digit, plot_glyph

glyph = glyph_for_digit(Scheme.S60, 12)
plot_glyph(glyph)
```

## Project layout

```
src/glyphs/
  scheme.py      # Scheme.S60 / S64
  placement.py   # six arm slots (bitmap bits)
  encoding.py    # digit ↔ placements
  glyph.py       # Glyph dataclass
  stroke.py      # curve sampling
  plot.py        # Matplotlib rendering
  display.py     # backends / save
tests/
```

## Development

```bash
pytest
ruff check src tests
```

### WSL

If no GUI backend is available, plots are saved automatically; see earlier notes on `python3-tk` or use `-o out.png`.
