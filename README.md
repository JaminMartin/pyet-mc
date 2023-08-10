# pyet-mc
Collection of tools for modelling the energy transfer processes in lanthanide-doped materials. 

Contains functions for visualising crystal structure around a central donor ion, subroutines for nearest neighbour probabilities and monte-carlo based multi-objective fitting for energy transfer.

# Install
WIP

# Use 
Firstly a .cif file must be provided. How you provide this .cif file is up to you! for this example we will take a .cif file from the materials project website. However they do also provide a convenient API that can also be used to provide cif data and is highly recomended as it also provides additional functionality such as XRD patterns etc. Information on how to access this API can be found here https://next-gen.materialsproject.org/api. 
```python
 KY3F10 = Structure(cif_file= 'KY3F10_mp-2943_conventional_standard.cif')

```
We then need to specify a central ion which all subsequent information will be calculated in relation to. 
```python
KY3F10.centre_ion('Y')

```
This will set the central ion to be a Ytrrium ion and yields the following output:
```
Central ion is Y
```
Now we can request some infomation! We can now query what ions and how far away they are from that central ion within a given radius. 
This can be done with the following:

```python
 KY3F10.nearest_neighbours_info(3.2)
``` 
Output:
```
Nearest neighbors within radius 3.2 Angstroms of a Y ion:
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom

```

