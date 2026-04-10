# Installation

`pyet-mc` is available on [PyPI](https://pypi.org/project/pyet-mc/) with pre-built wheels for Linux, macOS, and Windows. It requires **Python 3.13** or newer.

## Quick Install

Choose whichever environment manager you prefer — the examples below cover **conda** (via [miniforge](https://github.com/conda-forge/miniforge)) and **uv**.

### Using conda

Create and activate a new environment, then install `pyet-mc`:

```bash
conda create -n pyet python=3.13
conda activate pyet
pip install pyet-mc
```

> **Note:** If you encounter dependency issues (particularly with `numpy` or `matplotlib`), install them from conda-forge first:
> ```bash
> conda install -c conda-forge numpy matplotlib
> pip install pyet-mc
> ```

### Using uv

[uv](https://docs.astral.sh/uv/) is a fast, modern Python package manager. If you don't have it yet, see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

Create a new project directory and add `pyet-mc` as a dependency:

```bash
uv init my-project --python 3.13
cd my-project
uv add pyet-mc
```

This creates a `pyproject.toml`, sets up a virtual environment, and installs `pyet-mc` along with all its dependencies. You can then run your scripts with:

```bash
uv run my_script.py
```

## Verify the Installation

Create a new Python file (not inside the `pyet-mc` source tree) and try the following imports:

```python
from pyet_mc.structure import Structure, Interaction
from pyet_mc.fitting import Optimiser, general_energy_transfer
from pyet_mc.pyet_utils import Trace, cache_reader, cache_list, cache_clear
from pyet_mc.plotting import Plot
```

If no errors appear, `pyet-mc` is ready to use. 🎉

## Building From Source

Building from source is useful if you want to hack on `pyet-mc` itself or need a build for an unsupported platform. This requires the **Rust** toolchain and **maturin**.

### Prerequisites

1. Install [Rust](https://rustup.rs/) (via `rustup`).
2. Install [maturin](https://www.maturin.rs/) — it will be pulled in automatically by the build, but you can also install it explicitly.

### With uv (recommended)

```bash
git clone https://github.com/JaminMartin/pyet-mc.git && cd pyet-mc
uv venv --python 3.13
source .venv/bin/activate
uv sync
maturin develop --uv --release
```

### With conda

```bash
git clone https://github.com/JaminMartin/pyet-mc.git && cd pyet-mc
conda create -n pyet-dev python=3.13
conda activate pyet-dev
pip install maturin
maturin develop --release
```

The compiled extension module is installed directly into your active virtual environment — the location of the cloned repository does not matter.