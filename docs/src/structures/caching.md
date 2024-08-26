# A note on caching
As these calculations can be quite time-consuming for large iterations, and for said large iterations, the difference between runs should be minimal, caching was implemented to speed up subsequent runs.

When first used, pyet will create a cache directory. All interaction simulations will cache their interaction components along with info regarding the simulation conditions in JSON format. The generated JSON file is named in the following convention:

```
process_radius_concentration_interactiontype_iterations_intrinsic_timedatestamp.json
```
Resulting in a file name: 
```
singlecross_10_2pt5_DQ_1000_intrinsic_False_20240827080449.json
```
When generating interaction components it also takes note of the `.cif` file used, that way you can have multiple interaction components of identical parameters, but from different crystal structures. 

We can query and return the interaction components of the JSON file with the following code:
```python
from pyet.pyet_utils import cache_reader, cache_clear, cache_list

interaction_components2pt5pct = cache_reader(process = 'singlecross', radius = 10 , concentration = 2.5 , iterations = 50000 , interaction_type = 'DQ', intrinsic = False, sourcefile = "KY3F10.cif")
interaction_components5pct =  cache_reader(process = 'singlecross', radius = 10 , concentration = 5 , iterations = 50000 , interaction_type = 'DQ', intrinsic = False, sourcefile = "KY3F10.cif")
```
If what you have specified is not found in the cache, there will be a console log such as this:
```
File not found, check your inputs or consider running a simulation with these parameters
```
This will also return a None type, which must be handled accordingly, such as using a Python match statement. However, most likely you won't run into this as the `Interaction.sim_single_cross()` method implements this before it runs anyway. If the query does return, it will return a Numpy array of our interaction components. In that case, the following is also displayed:

```
file found in cache, returning interaction components
```
Following a major update to pyet-mc, it is also recommended that you clear the cache in the event a bug is discovered in the existing code. This will be highlighted in any release notes.

This can be done using:
```python
cache_clear()
```
This will prompt you if you are sure you would like to delete the cache.
```
Are you sure you want to delete all the cache files? [Y/N]?
```
You can also specify a file of a given simulation configuration, as was done above. In the event, you may have made a mistake and forgot to change a .cif file etc. It happens to the best of us...

If you want to know the status of your cache, you can also use the cache list to get the details, including file names and sizes. Like cache_clear(), a simple command is all you need!

```python
cache_list()
```

```
#======# Cached Files #======#
[0] singlecross_10_2pt5_DQ_1000_intrinsic_False_20240827080449.json (18017 bytes), Source file: KY3F10.cif, Date created: 2024-08-27T08:04:49.396355
[1] singlecross_10_5pt0_DQ_1000_intrinsic_False_20240827080449.json (20593 bytes), Source file: KY3F10.cif, Date created: 2024-08-27T08:04:49.622935
Total cache size: 0.04 MB
Run "cache_clear()" to clear the cache
#============================#
```

You can then delete a selected file like so:

```
cache_clear(0)
File to delete: singlecross_10_2pt5_DQ_1000_intrinsic_False_20240827080449.json Source file: KY3F10.cif, Date created: 2024-08-27T08:04:49.396355
Are you sure you want to delete this file? [Y/N]
y
Deleted file: singlecross_10_2pt5_DQ_1000_intrinsic_False_20240827080449.json

```
