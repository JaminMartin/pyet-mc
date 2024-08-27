# Installation
 Installation
Currently, pyet is not on the PyPI package repository; this will be the case until this project is more stable. It is still a work in progress. However, if you do wish to use pyet in its current form, it is as simple as the following:

Setup a new Python virtual environment (I recommend Conda, via [miniforge]()) and specify Python 3.11. The conda recomendation stems from the depedencies of this project, outlined below. 

```
conda create --name 'name of your env' python=3.11
```

Activate this virtual environment with "conda activate 'name of your env'". This ensures the package doesn't overwrite any of your existing Numpy/Scipy `Python` libraries
There are two options to install this package either through the provided wheels or building from source. Building from source will require the `rust` compiler and `maturin` to be installed.
The most straightforward way is to do, simply download the latest release build from the GitHub repository. 

then after activating your conda or environment manager of your choice simply 

```
pip install pyet-mc
```

If you encounter any issues, this may be due to `pymatgen` recommending you install its `numpy` and `matplotlib` dependencies via conda first.

```
conda install numpy matplotlib
```

pyet should now successfully be installed! 


To test that this was successful, create a new Python file (wherever you would like to use pyet-mc, not from within the pyet-mc source code).
Try to import pyet; assuming no error messages appear, pyet has been successfully installed in your virtual environment

```python
from pyet_mc.structure import Structure, Interaction
from pyet_mc.fitting import Optimiser, general_energy_transfer
from pyet_mc.pyet_utils import Trace, cache_reader, cache_list, cache_clear
from pyet_mc.plotting import Plot
```

## Building From Source

If you prefer, you can build from source. 

Firstly, ensure you have the `rust` toolchain and `maturin` installed. You can install it directly into your virtual environment you plan to use with this project by running:

```bash
conda activate "name of your env"
git clone git@github.com:JaminMartin/pyet-mc.git && cd pyet-mc 
maturin develop --release
```
The location of this does not matter as it is installed into the virtual environment. 