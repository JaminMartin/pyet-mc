# Adding your own interaction model
Adding your own model should be relatively straightforward. 
In the above code, we call the: `.sim_single_cross` method. You can add a different interaction method simply by defining a new function that can inherit the properties of the `Interaction` class e.g. 

```python
def sim_cooperative_energy_transfer(self, arg1, arg2, argn):
    # your code here # or you could write in in C or Rust and import it here

crystal_interaction = Interaction(KY3F10) # as shown before 
crystal_interaction.sim_cooperative_energy_transfer = sim_cooperative_energy_transfer
```

We can then use this method as the above default example.