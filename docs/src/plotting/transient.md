# Transient plots
The figures plotted using the `transient` plot type have been shown extensively in the section on [fitting](../fitting/fitting.md#fitting-experimental-data-to-energy-transfer-models) however it is worth discussing the purpose and limitations of this plot type.

The goal of this plot type is to quickly plot transients on an appropriate log scale for easy interpretation. It does, however, have its limitations - It may not correctly display this data, if so you may have to look at setting custom `x,y` axis limits. It then plots ~3 orders of magnitude on the `y-axis` and the `x-axis` limits are set from zero to the maximum value of your data. The `x-axis` label default is milliseconds; however, as was the case for the spectra plot, this can be easily [reconfigured](configuration.md) to an appropriate time base.

The `transient` plot type is designed to handle either `x,y` data as might be returned from the fitting process, for example, or it can take a `Trace`. This was to minimise code/data duplication. If you have defined a `Trace` for your data and given it a name, you can pass this in directly without having to worry about providing any `y` values.

## Subtracting offsets

When plotting fitted results on a log scale, you may notice that the fit curves bend downward at long time scales. This is not a fitting error. It happens because the energy transfer model includes a constant offset term, and at long times the exponential part of the signal decays away leaving just that offset. On a log scale this constant dominates and creates a visible bend or plateau in the tail of the curve.

To handle this, the `transient` method accepts an `offset` parameter. This subtracts a baseline value from the y-data before plotting, removing the constant term that causes the visual artifact.

```python
rdict = res.x

fig = Plot()
# Subtract the fitted offset from data and fit curves
fig.transient(trace2pt5pct, offset=rdict["offset1"])
fig.transient(time, fit1, fit=True, name="fit 2.5%", offset=rdict["offset1"])
fig.show()
```

The offset defaults to `0.0` so existing code is unaffected.

### Normalised data

If you have normalised your data (e.g. dividing by `np.max(fit)`) you will likely find the offset subtraction is not necessary. Normalising pushes the offset so far from the log scale floor that it has no visible effect. In that case you can just plot as normal:

```python
fig.transient(time, fit1 / np.max(fit1), fit=True, name="fit 2.5%")
```

If for some reason you still need to subtract it on normalised data, the normalised offset is simply the raw offset scaled by the same factor:

```python
norm_offset = rdict["offset1"] / np.max(fit1)
fig.transient(time, fit1 / np.max(fit1), fit=True, name="fit 2.5%", offset=norm_offset)
```

## Disabling the log scale

By default, calling `show()` on a transient plot forces the y-axis to a log scale. If you would rather see a linear y-axis (for example, to inspect the offset behaviour directly) you can disable this:

```python
fig.show(log_y=False)
```

This can be useful for debugging fits or when plotting data where a log scale is not appropriate. The default is `log_y=True` so existing code behaves the same as before.