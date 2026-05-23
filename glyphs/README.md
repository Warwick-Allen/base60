# glyphs

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
glyphs --demo
```

Or invoke the module directly:

```bash
python -m glyphs --demo
```

Save to a file explicitly (works everywhere, including headless WSL):

```bash
glyphs --demo -o demo.png
```

### WSL and graphical backends

On Ubuntu WSL, Matplotlib often defaults to the non-interactive **Agg** backend even when `DISPLAY` is set (for example under WSLg). Without a GUI toolkit, `plt.show()` cannot open a window.

If `glyphs --demo` cannot find an interactive backend, it saves `glyphs-demo.png` in the current directory and prints the path.

For an interactive window, install Tk support for your system Python (the venv uses it):

```bash
sudo apt install python3-tk
```

Then run `glyphs --demo` again from a session with `DISPLAY` set (WSLg and most X11 setups do this automatically). Alternatively, keep using `-o` to write PNG files and open them from Windows or your file manager.

## Project layout

```
src/glyphs/     # package source
tests/         # tests (pytest)
```

## Development

```bash
pytest
ruff check src tests
```
