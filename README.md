# pyet-mc
Collection of tools for modelling the energy transfer processes in lanthanide-doped materials. 

Contains functions for visualising crystal structure around a central donor ion, subroutines for nearest neighbour probabilities and monte-carlo based multi-objective fitting for energy transfer rates. This package aims to streamline the fitting process while providing useful tools to obtain quick structural information. The core function of this library is the ability to simultaneously fit lifetime data for various concentrations to tie down energy transfer rates more accurately. This allows one to decouple certain dataset features, such as signal offset/amplitude, from physical parameters, such as radiative and energy transfer rates. This is all handled by a relatively straightforward API wrapping the Scipy Optimise library.
<p align="center">
 <img width="602" alt="example lifetime and energy transfer fitting plot" src="https://github.com/JaminMartin/pyet-mc/assets/33270052/0716c0b9-73e1-4d4a-90db-69ed73eaf982">
</p>

## Table of Contents
- [Install](#install)
- [Use](#use)
  - [Generating a structure & plotting](#generating-a-structure--plotting)
  - [Modelling energy transfer](#modelling-energy-transfer)


# Install
WIP
# Use 

## Generating a structure & plotting
Firstly a .cif file must be provided. How you provide this .cif file is up to you! We will take a .cif file from the materials project website for this example. However, they also provide a convenient API that can also be used to provide cif data. It is highly recommended as it also provides additional functionality such as XRD patterns, etc. Information on how to access this API can be found here https://next-gen.materialsproject.org/api. 
We can create our structure with the following code. However, this may differ if you are using the materials project API. 
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
Now we can request some information! We can now query what ions and how far away they are from that central ion within a given radius. 
This can be done with the following:

```python
 KY3F10.nearest_neighbours_info(3.2)
``` 
Output:
```
Nearest neighbours within radius 3.2 Angstroms of a Y ion:
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom

```
We can then plot this if we would like, but we will increase the radius for illustrative purposes. We can use the inbuilt plotting to this.
```python
 KY3F10.structure_plot(5)   
```
Which yields the following figure:
<p align="center">
<img width="610" alt="plot using pyetmc library" src="https://github.com/JaminMartin/pyet-mc/assets/33270052/afa0370c-1fe2-4855-942a-8009e06ffdca">
</p>


We can also specify a filter only to show ions we care about. For example, we may only care about the fluoride ions. 
```python
filtered_ions = ['F']

KY3F10.structure_plot(5, filter = filtered_ions)  
```
This gives us a filtered plot:
<p align="center">
<img width="610" alt="filtered plot" src="https://github.com/JaminMartin/pyet-mc/assets/33270052/8c44b3c1-8451-4862-99ea-d331d8edc092">
</p>

In future, the colours will be handled based on the ion, much like the materials project and moved to plotly, the current plotting is purely a placeholder for functionality. This is a WIP.
## Modelling energy transfer 
