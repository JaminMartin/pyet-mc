# Weighted Fitting

There is also the ability to have the fitting process weight each trace differently, as well as adjust the weighting of all traces when their length is not even. Take, for example, the case where we have two traces of different lengths. We can generate this as before with some slight modifications.

```python
if __name__ == "__main__":
    from pyet.fitting import general_energy_transfer
    # generate some random data
    time_1050 = np.arange(0,21,0.02) #1050 data points 0 to 21ms
    time_525 = np.arange(0,21,0.04) #525 data points 0 to 21ms
    #Generate some random data based on our provided constants and time basis
    data_2pt5pct = general_energy_transfer(time_1050, interaction_components2pt5pct, const_dict1)
    data_5pct = general_energy_transfer(time_525, interaction_components5pct, const_dict2)
    #Add some noise to make it more realistic
    rng = np.random.default_rng()
    noise_1050 = 0.01 * rng.normal(size=time_1050.size)
    noise_525 = 0.01 * rng.normal(size=time_525.size)
    data_2pt5pct = data_2pt5pct + y_noise
    data_5pct = data_5pct + y_noise
```
This is much the same as before, but now we have two datasets of different lengths. If we try to fit this by trying to minimise the Residual Sum of Squares (RSS) (which this library uses) the fit would be intrinsically biased to the dataset of longer length. We could instead use the Mean Squared Error (MSE) to account for this, but MSE is subject to biasing from outlier data. Instead, we add an appropriate weighting to the smaller datasets so that their contribution is proportional to that of the longer dataset. This method requires the assumption all data sets have a similar variance, which is fair for these kinds of measurements with good signal quality and high numbers of averages. This gives us a Weighted Residual Sum of Squares (WRSS) implementation. This re-weighting of data is implemented as a default method in the fitting optimiser class. So if we re-ran the fit with this new dataset we would see this output during the fit:

```
the weights of the 2.5% trace has been adjusted to 1.0
the weights of the 5% trace has been adjusted to 2.0
['amp1', 'amp2', 'cr', 'rad', 'offset1', 'offset2']
Guess with initial params:{'amp1': 1, 'amp2': 1, 'cr': 100, 'rad': 0.5, 'offset1': 0, 'offset2': 0}
Started fitting...
```

This aims to compensate for the discrepancy in the number of data points. However, it can be turned off if it is not a desired feature simply by changing the instantiation of the optimiser to have `auto_weighting` set to `False`. 
```python
opti = Optimiser([trace2pt5pct,trace5pct],[params2pt5pct,params5pct], model = 'default', auto_weights = False)
```

There is also the ability to set a per-trace weighting to each `Trace` so that it intentionally biases the fitting process to try to either fit more or less to that data set. This is useful in the case where we have less than ideal data that we don't want to influence the fit or in the case we have ideal data that we want to fit more heavily to. To add a weighting factor to a trace it is as simple as declaring that when we create our `Trace` objects. Let's imagine the case where we want to weight our smaller dataset further for some contrived reason. We can simply add a weighting to that `Trace`. Note that by default the weighting is set to one. 
```python
trace2pt5pct = Trace(data_2pt5pct, time,  '2.5%', interaction_components2pt5pct)
trace5pct = Trace(data_5pct, time, '5%', interaction_components5pct, weighting = 5)
```

This would yield the following when fitting:

```
the weights of the 2.5% trace have been adjusted to 1.0
the weights of the 5% trace have been adjusted to 10.0
['amp1', 'amp2', 'cr', 'rad', 'offset1', 'offset2']
Guess with initial params:{'amp1': 1, 'amp2': 1, 'cr': 100, 'rad': 0.5, 'offset1': 0, 'offset2': 0}
Started fitting..
```
As you can see, the weighting has actually been adjusted to 10; this is due to the automatic re-weighting ensuring the weighting we provide is a weighting for _equal_ datasets. If you don't want to use the automatic re-weighting but restain your weighting of `5` you can simply turn off automatic re-weighting as discussed.

There is no right or wrong way to implement these weights and should be addressed on a case-by-case basis, as they can heavily influence your fitted parameters.
