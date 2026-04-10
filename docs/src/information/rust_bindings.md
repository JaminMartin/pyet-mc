# Rust Bindings

pyet-mc includes a Rust extension module that provides a faster implementation of the energy transfer model. If you installed from PyPI, the extension is bundled in the wheel and ready to go.

## Using the Rust backend

Pass `model='rs'` when creating your `Optimiser`:

```python
opti = Optimiser([trace1, trace2], [params1, params2], model='rs')
```

This uses a parallel Rust implementation that splits the computation across your CPU cores using [Rayon](https://github.com/rayon-rs/rayon). For large datasets (many time points, high iteration counts, multiple traces) this is noticeably faster than the pure Python/NumPy version and uses less memory.

## Single-threaded mode

The parallel version will use all available cores by default. If that is consuming too many resources or you are running multiple fits at once, you can use the sequential Rust implementation instead:

```python
opti = Optimiser([trace1, trace2], [params1, params2], model='rs_single')
```

This gives you the same performance benefits over Python (no intermediate array allocations, tight loop) without the parallelism. It is a good choice when you want the Rust speedup but need to keep CPU usage under control.

## Summary

| Model | Backend | Parallelism |
|-------|---------|-------------|
| `'default'` | Python/NumPy | No |
| `'rs'` | Rust (Rayon) | Yes, across time points |
| `'rs_single'` | Rust | No |

## What if the extension isn't available?

If the Rust module can't be imported (unsupported platform, source build without Rust, etc.) you will see a warning on import and `model='default'` will still work fine. Only `model='rs'` and `model='rs_single'` require the extension.

If you need to build it yourself, see the [installation docs](../introduction/installation.md#building-from-source). You will need the Rust toolchain and maturin.