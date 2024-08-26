# Road Map

- ~~Migrate a lot of the plotting functionality to `Plotly` and wrap it in a matplotlib-like GUI. This work has started, an example of this transition can be found [here](#generating-a-structure--plotting) & [here](#fitting-experimental-data-to-energy-transfer-models).~~ ✅ 
- ~~Update structure figures to use Jmol colour palette. Correct atom colours are coming soon!~~
- ~~Move compute-heavy / memory-intensive functions to Rust for better performance.~~
- Add more interaction types, e.g., cooperative energy transfer and other more complex energy transfer processes. 
- Add geometric correction factors and shield factors for various crystal structures and ions [[2](../information/references.md#2)]. 
- Add alternative to Monte Carlo methods e.g. the shell model(performance vs accuracy tests required). If successful, the shell model could improve performance greatly [[3](../information/references.md#3),[4](../information/references.md#4)].
- ~~Move docs to MDbook for continuous integration.~~
- Optional open-source database where results can be stored, retrieved, and rated based on data quality and fit, much like the ICCD crystallography database. 
- Add more tests; this will be important as the project grows and other users want to add features. 
