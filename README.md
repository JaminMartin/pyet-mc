# pyet-mc
Collection of tools for modelling the energy transfer processes in lanthanide-doped materials. 

Contains functions for visualising crystal structure around a central donor ion, subroutines for nearest neighbour probabilities and monte-carlo based multi-objective fitting for energy transfer.

<img width="611" alt="image" src="https://github.com/JaminMartin/pyet-mc/assets/33270052/9424c2cc-0b9a-4e7d-9343-add50900c3d5">

# Use 
Firstly a .cif file must be provided. How you provide this .cif file is up to you! for this example we will take a .cif file from the materials project website. However they do also provide a convenient API that can also be used to provide cif data and is highly recomended as it also provides additional functionality such as XRD patterns etc. Information on how to access this API can be found here https://next-gen.materialsproject.org/api. 
```python
 KY3F10 = Structure(cif_file= 'KY3F10_mp-2943_conventional_standard.cif')

```
We then need to specify a central ion which all subsequent information will be calculated in relation to. 
```python
KY3F10.centre_ion('Y')

```
This will set the central ion to be a Ytrrium ion and yields the following output
> Output: Central ion is Y


