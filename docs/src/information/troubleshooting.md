# Troubleshooting
- pyet is using too much memory:
  - this is a known issue. Numpy does not seem to free up its arrays fast enough, so it can consume a lot of memory. For example, a 50,000 iteration interaction component and 15,000 time points will consume 6GB of memory. This is why this library does not use pre-allocation, as it is too easy to accidentally run out of memory and use swap memory, slowing things down further. I have a Rust implementation that does not suffer from this issue due to better memory management; This will be part of future releases.
- pyet is slow:
  - this is also a known issue. This boils down to the number of exponential calls. This is documented here: https://github.com/JaminMartin/pyet-mc/issues/2

The latter two of these issues have been addressed by including `Rust` bindings described [here](./rust_bindings.md).  

- pyet does not converge to a good fit
  -  This could be for a multitude of reasons. The most probable is either the tolerance for the fit or the fitting algorithm. Try decreasing your tolerance and trying some different methods. Global optimise will soon be available to help remedy the need for good initial guesses. The concentration specified for the interaction component may not be accurate; this, alongside the cross-relaxation parameter being coupled to all traces, may cause an inability to converge. Try to fit with them uncoupled. If you continue to have trouble just reach out! there could be a bug in my code!
