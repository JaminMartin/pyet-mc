# Fitting Algorithms

Under the hood, pyet-mc wraps [scipy.optimize](https://docs.scipy.org/doc/scipy/reference/optimize.html) to do all of its fitting. The `Optimiser.fit()` method lets you pick a solver and pass any extra `*args` or `**kwargs` straight through to the underlying scipy function. This means anything scipy supports (tolerances, callback functions, method selection, etc.) you can use directly.

The basic signature looks like this:

```python
res = opti.fit(guess, bounds=None, solver="minimize", *args, **kwargs)
```

- `guess` is a dictionary of your initial parameter values.
- `bounds` is an optional dictionary of `(min, max)` tuples (required for some solvers).
- `solver` is a string selecting which scipy solver to use.
- Everything else gets forwarded to scipy.

## Solvers

### `minimize`

This is the default solver and the one you will probably use most often. It calls `scipy.optimize.minimize` and supports all of its local optimization methods (Nelder-Mead, L-BFGS-B, Powell, etc.) via the `method` keyword argument.

**Bounds:** Not passed to scipy by this solver. If you need bounded local optimization, pick a method that handles bounds internally (like L-BFGS-B) and pass them through `**kwargs`.

**When to use it:** You have a reasonable initial guess and want a fast, reliable local fit.

```python
guess = {'amp1': 1, 'amp2': 1, 'cr': 100, 'rad': 0.5, 'offset1': 0, 'offset2': 0}

# Nelder-Mead is a solid default choice
res = opti.fit(guess, solver="minimize", method='Nelder-Mead', tol=1e-13)

# Or try Powell for a different local search strategy
res = opti.fit(guess, solver="minimize", method='Powell', tol=1e-12)
```

Since `"minimize"` is the default solver, you can also just omit it:

```python
res = opti.fit(guess, method='Nelder-Mead', tol=1e-13)
```

### `basinhopping`

Calls `scipy.optimize.basinhopping`. This is a global optimization method that combines random perturbation of coordinates with local minimization. It is good at escaping local minima.

**Bounds:** Not required (not passed to scipy by this solver).

**When to use it:** Your initial guess might not be close to the true solution, or the cost surface has lots of local minima. It is slower than `minimize` but more robust.

```python
guess = {'amp1': 1, 'amp2': 1, 'cr': 200, 'rad': 1.0, 'offset1': 0, 'offset2': 0}

res = opti.fit(guess, solver="basinhopping", niter=100, T=1.0)
```

Here `niter` and `T` (temperature) are forwarded directly to `scipy.optimize.basinhopping`.

### `differential_evolution`

Calls `scipy.optimize.differential_evolution`. This is a stochastic population-based global optimizer. It explores the parameter space broadly, so it can find solutions even when your guess is poor.

**Bounds:** Required. You must provide a `bounds` dictionary.

**When to use it:** You have little idea where the solution is, but you can define a reasonable search region. It is thorough but can be slow for high-dimensional problems.

```python
guess = {'amp1': 1, 'amp2': 1, 'cr': 200, 'rad': 1.0, 'offset1': 0, 'offset2': 0}

bounds = {
    'amp1': (0, 2),
    'amp2': (0, 2),
    'cr': (1, 1000),
    'rad': (0.01, 10),
    'offset1': (-0.1, 0.1),
    'offset2': (-0.1, 0.1),
}

res = opti.fit(guess, bounds=bounds, solver="differential_evolution", tol=1e-10)
```

The guess is used as the `x0` starting point within the bounded region.

### `dual_annealing`

Calls `scipy.optimize.dual_annealing`. This is another global optimization method inspired by simulated annealing. It balances exploration of the search space with refinement near promising solutions.

**Bounds:** Required. You must provide a `bounds` dictionary.

**When to use it:** Similar situations to `differential_evolution`. Dual annealing can sometimes converge faster depending on the problem. Worth trying if differential evolution is too slow or gets stuck.

```python
guess = {'amp1': 1, 'amp2': 1, 'cr': 200, 'rad': 1.0, 'offset1': 0, 'offset2': 0}

bounds = {
    'amp1': (0, 2),
    'amp2': (0, 2),
    'cr': (1, 1000),
    'rad': (0.01, 10),
    'offset1': (-0.1, 0.1),
    'offset2': (-0.1, 0.1),
}

res = opti.fit(guess, bounds=bounds, solver="dual_annealing", maxiter=1000)
```

## Bounds Format

When you need to pass bounds, provide a dictionary where the keys match your guess dictionary and the values are `(min, max)` tuples:

```python
bounds = {
    'amp1': (0, 2),       # amplitude between 0 and 2
    'cr': (1, 1000),      # cross-relaxation rate between 1 and 1000
    'rad': (0.01, 10),    # radiative rate between 0.01 and 10
    'offset1': (-0.5, 0.5),
}
```

The keys in `bounds` should match the keys in your `guess` dictionary. For `differential_evolution` and `dual_annealing`, you need bounds for every parameter. If you leave `bounds` out (or pass `None`), it defaults to an empty dictionary, which is fine for `minimize` and `basinhopping`.
