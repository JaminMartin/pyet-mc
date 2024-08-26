# Saving plots
Under the hood, pyet-mc's plotting library leverages `Plotly`'s saving method, therefore it is very simple to save a figure.
We provide a save path and file name with the appropriate file extension (e.g. `.svg`, `.pdf` for a full list consult the `Plotly` documentation [here](https://plotly.com/python/static-image-export/))
```python
path = '/path/to/store/'
name = 'file.svg'
figure.save(path, name)
```
If any errors arise from the plotting, it is again best to consult the `Plotly` documentation regarding [saving figures](https://plotly.com/python/static-image-export/), as it may require installing the `kaleido` package separately.