# gyphs

Python toolkit for glyph plotting and visualisation, built on [NumPy](https://numpy.org/) and [Matplotlib](https://matplotlib.org/).

## Requirements

- Python 3.10+

## Setup

Create a virtual environment and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Run the demo plot to confirm dependencies are working:

```bash
gyphs --demo
```

Or invoke the module directly:

```bash
python -m gyphs --demo
```

## Project layout

```
src/gyphs/     # package source
tests/         # tests (pytest)
```

## Development

```bash
pytest
ruff check src tests
```
