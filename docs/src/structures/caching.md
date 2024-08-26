# A note on caching
As these calculations can be quite time-consuming for large iterations, and for said large iterations, the difference between runs should be minimal, caching was implemented to speed up subsequent runs.

When first used, pyet will create a cache directory. All interaction simulations will cache their interaction components along with info regarding the simulation conditions in JSON format. The generated JSON file is named in the following convention:

```
process_radius_concentration_interactiontype_iterations_intrinsic.json
```
Resulting in a file name: 
```
singlecross_20_2pt5_DQ_50000_intrinsic_False
```
We can query and return the interaction components of the JSON file with the following code:
```python
from pyet.pyet_utils import cache_reader, cache_clear, cache_list

interaction_components2pt5pct = cache_reader(process = 'singlecross', radius = 10 , concentration = 2.5 , iterations = 50000 , interaction_type = 'DQ', intrinsic = False)
interaction_components5pct =  cache_reader(process = 'singlecross', radius = 10 , concentration = 5 , iterations = 50000 , interaction_type = 'DQ', intrinsic = False)
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
singlecross_10_2pt5_DQ_50000.json (958053 bytes)
singlecross_10_5_DQ_50000.json (1121375 bytes)
Total cache size: 2.08 MB
Run "cache_clear()" to clear the cache
#============================#
```