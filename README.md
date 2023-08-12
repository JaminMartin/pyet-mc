<p align="center">

# pyet-mc

</p>

<p align="center">
 <img width="602" alt="example lifetime and energy transfer fitting plot" src="https://github.com/JaminMartin/pyet-mc/assets/33270052/0716c0b9-73e1-4d4a-90db-69ed73eaf982">
</p>

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [Generating a structure & plotting](#generating-a-structure--plotting)
  - [Energy transfer models](#energy-transfer-models)
    - [Modelling energy transfer processes](#modelling-energy-transfer-processes)
    - [A note on caching](#a-note-on-caching)
    - [Adding your own energy transfer model](#adding-your-own-energy-transfer-model)
  - [Fitting experimental data to energy transfer models](#fitting-experimental-data-to-energy-transfer-models)
- [Referencing this project](#referencing-this-project)  
- [License](#license)

# Introduction
Collection of tools for modelling the energy transfer processes in lanthanide-doped materials. 

Contains functions for visualising crystal structure around a central donor ion, subroutines for nearest neighbour probabilities and monte-carlo based multi-objective fitting for energy transfer rates. This package aims to streamline the fitting process while providing useful tools to obtain quick structural information. The core function of this library is the ability to simultaneously fit lifetime data for various concentrations to tie down energy transfer rates more accurately. This allows one to decouple certain dataset features, such as signal offset/amplitude, from physical parameters, such as radiative and energy transfer rates. This is all handled by a relatively straightforward API wrapping the Scipy Optimise library.

# Installation
WIP
# Usage 

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
## Energy transfer models
$$I_j(t) = e^{-(\gamma_r + \gamma_{tr,j})t}$$
for a single step cross relaxation process (currently the only model implemented) $\gamma_{tr,j}$ takes the form: 
```math
\gamma_{tr,j} = C_{cr} \sum_i \left(\frac{R_0}{R_i}\right)^s
```




$\gamma_{av}$, i.e an average energy transfer rate may be defined as $\frac{1}{n}\sum_{j=1}^n \gamma_{tr,j}$. 
### Modelling energy transfer processes
Note: Currently, there is only one energy transfer process implemented and so this section may be subject to change in future releases. 

Consider our crystal structure we previously generated. We wish to now "dope" that structure with some lanthanide ions randomly around some central donor ion. We will replace our previously defined "central yttrium atom" with samarium. We will then randomly (based on the concentration of the dopant in the crystal) dope samarium ions around this central samarium ion. This step needs to performed many times in order to "build up" many random unique samarium-samarium donor-acceptor configurations. When the number of random configurations is large enough, this should accurately represent a physical crystal sample. This is the Monte-Carlo aspect of our energy transfer analyis. 

To generate our random samples we utilise the interaction class. This class takes in our structure class and provides additional methods for calculating our interaction components as well as more specific plotting methods for doped crystals. We can simply inact this class simply by passing our structure to the interaction class:
```python
crystal_interaction = Interaction(KY3F10)
```

```python
coords = inter.distance_sim(radius=10, concentration = 15, dopant='Sm')
```
This returns a list of radial distances in angstroms of the dopant samarium ions in relation to the central samarium donor ion.
```
[8.28402747 7.17592429 7.17592429 9.33368811 8.28402747 4.30030493
 8.28402747 7.17592429 9.33368811 7.17592429 3.98372254 8.28402747]
```

We can also take a more detailed look at what has happend by calling 
```python
print(coords.filtered_coords)
```
```
           r       theta           phi species
0   7.175924  115.071364 -1.156825e+02       Y
1   7.175924  115.071364 -1.543175e+02       Y
2   8.284027   90.000000 -1.350000e+02       Y
3   7.175924   66.886668 -1.525658e+02       Y
4   7.175924   66.886668 -1.174342e+02       Y
5   9.192125  109.317471 -1.800000e+02       Y
6   5.861968   92.188550 -1.800000e+02       Y
7   9.333688  162.434187 -1.800000e+02       Y
8   8.284027  135.000000  1.800000e+02      Sm
9   7.175924  115.071364  1.156825e+02      Sm
10  7.175924  115.071364  1.543175e+02       Y
11  4.300305  135.000000 -1.800000e+02       Y
12  3.983723   45.000000 -1.800000e+02       Y
13  7.175924   66.886668  1.525658e+02      Sm
14  9.333688   72.434187 -1.800000e+02      Sm
15  8.284027   45.000000 -1.800000e+02       Y
16  9.192125   19.317471 -1.800000e+02       Y
17  8.284027   90.000000  1.350000e+02       Y
18  7.175924   66.886668  1.174342e+02       Y
19  9.192125  109.317471 -9.000000e+01       Y
20  5.861968   92.188550 -9.000000e+01       Y
```
As we can see some of the yttrium ions have been replaced by samarium ions, as expected. 


### A note on caching
As these calculations can be quite time consuming for large iterations, and that for said large iterations the difference between runs should be minimal, caching was implemented to speed up subsequent runs.

When first used, pyet will create a cache directory. All interaction simulations will cache their interaction components along with info regarding the conditions of the simulation in JSON format. The generated JSON file is named in the following convention:

```
process_radius_concentration_interactiontype_iterations.json
```
We can query and return the interaction components of the JSON file with the following code:
```python
from pyet import helper_funcs as hf

conc2pt5pct = hf.cache_reader(process = 'singlecross', radius = 10 , concentration = 2.5 , iterations = 50000 , interaction_type = 'QQ')
conc5pct =  hf.cache_reader(process = 'singlecross', radius = 10 , concentration = 5 , iterations = 50000 , interaction_type = 'QQ')
```
If what you have specified is not found in the cache, there will be a console log such as this:
```
File not found, check your inputs or consider running a simulation with these parameters
```
This will also return a None type which will need to be handled accordingly, such as using a python match statement. This will be shown in a following section. If the query does return, it will return a Numpy array of our interaction components. In that case, the following is also displayed:

```
file found in cache, returning interaction components
```
Following a major update to pyet, it is also recomended that you clear the cache in the event a bug is discovered in the existing code. This will be highlighted in any release notes.

This can be done using:
```python
hf.cache_clear()
```
This will prompt you if you are sure you would like to delete the cache.
```
Are you sure you want to delete all the cache files? [Y/N]?
```
You can also specify a file of a given simulation configuration as was done above. In the event you may have made a mistake and forgot to change a .cif file etc. Happens to the best of us...

If you are wanting to know the status of your cache, you can also use cache list to get the details including file names and size. Like cache_clear(), a simple command is all you need!

```python
hf.cache_list()
```
```
#======# Cached Files #======#
singlecross_10_2pt5_QQ_50000.json (958053 bytes)
singlecross_10_5_QQ_50000.json (1121375 bytes)
Total cache size: 2.08 MB
Run "cache_clear()" to clear the cache
#============================#
```
### Adding your own energy transfer model
WIP
## Fitting experimental data to energy transfer models
Fitting of exerpimental lifetime transients to determine energy transfer parameters is the primary purpose of this library and so will utilise all the previous components covered. 
We will utilise some of our previously generated single step cross relaxation 

Recalling previously our two quadrapole-quadrapole datasets for 2.5% and 5% doping respectively, If you dont have these generatd interaction components please refer to [modelling energy transfer processes](#modelling-energy-transfer-processes) we can can use them to generate some arifical data given some additional parameters. 


# Referencing this project

# License
The project is licensed under the GNU GENERAL PUBLIC LICENSE.
