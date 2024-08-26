# Installation
Currently, pyet is not on the PyPI package repository; this will be the case until this project is more stable. It is still a work in progress. However, if you do wish to use pyet in its current form, it is as simple as the following:

Setup a new Python virtual environment (I recommend Conda) and specify Python 3.11 (This is required!)
```
conda create --name 'name of your env' python=3.11
```
Activate this virtual environment with "conda activate 'name of your env'". This ensures the package doesn't overwrite any of your existing Numpy/Scipy `Python` libraries
Clone this repository in a location of your choosing, or download it as a zip file and extract it
```
git clone git@github.com:JaminMartin/pyet-mc.git
```
In the terminal, cd into this directory and tell pip to install this package
```
path/to/my/package/ pip install . 
```
To test that this was successful, create a new Python file (wherever you would like to use pyet-mc, not from within the pyet-mc source code).

Try to import pyet; assuming no error messages appear, pyet has been successfully installed in your virtual environment
```python
from pyet.structure import Structure, Interaction
from pyet.fitting import Optimiser, general_energy_transfer
from pyet.pyet_utils import Trace, cache_reader, cache_list, cache_clear
from pyet.plotting import Plot
```