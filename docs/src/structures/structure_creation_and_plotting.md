# Generating a structure & plotting

**Note** a complete example of the following code can be found [here](https://github.com/JaminMartin/pyet-mc/tree/main/examples)
## Generating a structure & plotting
Firstly, a .cif file must be provided. How you provide this .cif file is up to you! We will take a .cif file from the materials project website for this example. However, they also provide a convenient API that can also be used to provide .cif data. It is highly recommended as it provides additional functionality, such as XRD patterns. Information on how to access this API can be found here: https://next-gen.materialsproject.org/api. 
We can create our structure with the following code. However, this may differ if you are using the materials project API. It is also important to ensure your .cif file is using the conventional standard. 
```python
KY3F10 = Structure(cif_file= 'KY3F10.cif')
```
We then need to specify a central ion, to which all subsequent information will be calculated in relation to. It is important to note, we must specify the charge of the ion as well.
```python
KY3F10.centre_ion('Y3+')
```
This will set the central ion to be a Ytrrium ion and yield the following output:
```
central ion is [-5.857692   -5.857692   -2.81691722] Y3+
with a nearest neighbour Y3+ at 3.914906764969714 angstroms
```
This gives us the basic information about the host material. 
Now we can request some information! We can now query what ions and how far away they are from that central ion within a given radius. 
This can be done with the following:

```python
KY3F10.nearest_neighbours_info(3.2)
``` 
Output:
```
Nearest neighbours within radius 3.2 Angstroms of a Y3+ ion:
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.227665 Angstrom
Species = F, r = 2.386628 Angstrom

```
We can plot this if we like, but we will increase the radius for illustrative purposes. We can use the inbuilt plotting for this.
```python
if __name__ == "__main__":
    fig1 = KY3F10.structure_plot(radius = 5)  
    fig1.show() 
```
Which yields the following figure:
<p align="center">
 <img width="700" alt="example lifetime and energy transfer fitting plot" src="../images/crystal_jmol.png">
</p>

It's worth noting here briefly that due to the way the `PyWebEngine` App is being rendered using the multiprocessing library, it is essential to include the `if __name__ == "__main__":` block. Unfortunately, until a different backend for rendering the `Plotly` `.html` files that also supports `javascript` this has to stay. 
We can also specify a filter only to show ions we care about. For example, we may only care about the fluoride ions. 
```python
if __name__ == "__main__":
  filtered_ions = ['F-', 'K+'] #again, note we must specify the charge!

  fig2 = KY3F10.structure_plot(radius = 5, filter = filtered_ions)  
  fig2.show() 
```
This gives us a filtered plot:
<p align="center">
 <img width="700" alt="example lifetime and energy transfer fitting plot" src="../images/filtered_crystal_jmol.png">
</p>

## Querying coordinates

The `nearest_neighbours_info()` method we used earlier is handy for a quick look at what's around the central ion, but it just prints text to the console. If you want the actual coordinate data for further analysis or custom workflows, there are two methods that return Pandas DataFrames.

`nearest_neighbours_coords(radius)` returns the Cartesian coordinates of all ions within the given radius:

```python
coords = KY3F10.nearest_neighbours_coords(3.2)
print(coords)
```
```
          x         y         z species
0 -7.430692 -4.284692 -2.816917      F-
1 -4.284692 -5.857692 -1.044117      F-
2 -4.284692 -5.857692 -4.589717      F-
...
```

The returned DataFrame has columns `x`, `y`, `z`, and `species`.

`nearest_neighbours_spherical_coords(radius)` returns spherical polar coordinates relative to the central ion:

```python
sph_coords = KY3F10.nearest_neighbours_spherical_coords(3.2)
print(sph_coords)
```
```
          r      theta        phi species
0  2.386628  90.000000 -135.00000      F-
1  2.227665  37.94576  -180.00000      F-
2  2.227665  142.05424 -180.00000      F-
...
```

The returned DataFrame has columns `r` (radial distance in Angstroms), `theta` (polar angle in degrees), `phi` (azimuthal angle in degrees), and `species`.

Think of `nearest_neighbours_info()` as the print-friendly summary and these two methods as the ones you reach for when you actually need the data, for example to feed into your own distance calculations, filtering logic, or visualisation code.

## R₀ and the nearest neighbour distance

You may have noticed this line in the output when we called `centre_ion()`:

```
with a nearest neighbour Y3+ at 3.914906764969714 angstroms
```

This comes from `get_R0()`, which is called automatically inside `centre_ion()`. You don't need to call it yourself. What it does is search for the closest ion of the same species as the central ion within 50 Angstroms and store that distance as `self.r0`.

This value, $R_0$, is the nearest-neighbour distance and plays a key role in the interaction component formula:

$$C_{cr} \sum_i \left(\frac{R_0}{R_i}\right)^s$$

The energy transfer rate between a donor and each acceptor ion at distance $R_i$ scales as $(R_0 / R_i)^s$, where $s$ depends on the interaction type (e.g. 6 for dipole-dipole, 8 for dipole-quadrupole). Because everything is normalised by $R_0$, the nearest-neighbour distance effectively sets the scale for how quickly the transfer rate drops off with distance. A closer nearest neighbour means a larger $R_0$ and stronger coupling at any given $R_i$.

If you ever need to inspect the value directly, it's available as an attribute after calling `centre_ion()`:

```python
print(KY3F10.r0)  # e.g. 3.914906764969714
```
