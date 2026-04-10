# Traces

The `Trace` class is a container for your experimental data. It bundles together the signal, time axis, a label, and the pre-calculated interaction components for a given concentration. This is the primary data structure you pass to the `Optimiser` for fitting and to the `Plot.transient()` method for plotting.

## Creating a Trace

A basic `Trace` requires four things: your y-data (signal), x-data (time), a name, and the interaction components for that concentration.

```python
from pyet_mc.pyet_utils import Trace

trace = Trace(ydata, xdata, 'my trace', interaction_components)
```

| Argument | Type | Description |
|----------|------|-------------|
| `ydata` | `np.ndarray` | The signal (y-axis) data points |
| `xdata` | `np.ndarray` | The time (x-axis) data points |
| `fname` | `str` | A label for the trace, used in plot legends |
| `radial_data` | `np.ndarray` | The interaction components for this concentration, as returned by `sim_single_cross()` or `cache_reader()` |
| `weighting` | `int` | Optional per-trace weighting for the fit. Defaults to `1` |
| `parser` | `str` or `False` | Optional data reduction method. Defaults to `False` (no parsing) |

## Data parsing

Real experimental data can be very densely sampled, particularly from oscilloscopes or time-correlated single photon counting systems. Fitting to hundreds of thousands of points is slow and often unnecessary. The `parser` option lets you thin out the data when constructing a `Trace` so the fitting runs faster without losing the important features of the decay.

There are three built-in parsers:

| Parser | What it does |
|--------|-------------|
| `'parse_10'` | Keeps every 10th data point |
| `'parse_100'` | Keeps every 100th data point |
| `'parse_log'` | Selects 500 points spaced logarithmically across the trace |

You specify the parser as a string when creating the `Trace`:

```python
trace = Trace(ydata, xdata, '5%', interaction_components, parser='parse_100')
```

Both the signal and time arrays are thinned by the same indices, so they stay aligned. If no parser is specified the full dataset is used.

### Choosing a parser

For most lifetime data, `'parse_100'` is a good starting point. It reduces a 100,000 point trace down to 1,000 points, which is usually more than enough to capture the shape of the decay while making the fit significantly faster.

The `'parse_log'` option is particularly useful for data that spans several orders of magnitude in time. It samples more densely at early times (where the signal changes rapidly) and more sparsely at late times (where the signal is slowly decaying). This gives better coverage of the fast initial dynamics without wasting points on the flat tail. It always returns 500 points regardless of the input length.

If you are unsure, try fitting with and without a parser and compare the results. The fitted parameters should be very similar. If they differ significantly it may be worth using a denser sampling or the full dataset.

### Example with real data

```python
import pandas as pd
from pyet_mc.pyet_utils import Trace

# Load experimental data from a CSV
data = pd.read_csv('lifetime_data.csv', header=None, names=['time', 'intensity'])

# Basic preprocessing
data.intensity = data.intensity - data.intensity.min()
data.time = data.time * 1000  # convert to ms

# Create a Trace with every 100th point
trace = Trace(
    data.intensity.to_numpy(),
    data.time.to_numpy(),
    '5% Sm:KY3F10',
    interaction_components,
    parser='parse_100'
)
```

## Weighting

Each `Trace` can carry a weighting that influences how much it contributes to the fit. This is covered in detail in the [weighted fitting](weighted_fitting.md) documentation, but in short you can set it at construction time:

```python
trace = Trace(ydata, xdata, '5%', interaction_components, weighting=5)
```

The default weighting is `1`. The `Optimiser` also has an `auto_weights` feature that adjusts weightings to compensate for traces of different lengths, which is enabled by default.

## Using Traces with the Optimiser

Once you have your `Trace` objects you pass them to the `Optimiser` along with the parameter names for each trace. See [general fitting](general_fitting.md) for the full workflow.

```python
from pyet_mc.fitting import Optimiser

params_2pt5 = ['amp1', 'cr', 'rad', 'offset1']
params_5 = ['amp2', 'cr', 'rad', 'offset2']

opti = Optimiser([trace_2pt5, trace_5], [params_2pt5, params_5], model='rs')
```

## Using Traces with plotting

The `transient()` plot method can accept a `Trace` directly. It will use the trace's time and signal data along with its name for the legend, so you don't have to pass these separately.

```python
from pyet_mc.plotting import Plot

fig = Plot()
fig.transient(trace_2pt5)  # uses trace.time, trace.trace, and trace.name
fig.transient(trace_5)
fig.show()
```

This is equivalent to calling `fig.transient(trace.time, trace.trace, name=trace.name)` but saves you the repetition. See the [transient plotting](../plotting/transient.md) docs for more on plotting options like offset subtraction and log scale control.