"""Tests for the fitting module.

Covers:
- general_energy_transfer (explicit dict keys)
- double_exp (explicit dict keys)
- Rust wrapper functions (_rust_energy_transfer, _rust_energy_transfer_para)
- Optimiser construction, wrss, fit, _run_solver, adjust_weights
- Solver dispatch (minimize, basinhopping, differential_evolution, dual_annealing)
- Error handling (unsupported solver, failed dict wrap)
"""

import os
import unittest
from unittest.mock import patch

import numpy as np
import scipy.optimize

from pyet_mc.fitting import (
    Optimiser,
    double_exp,
    general_energy_transfer,
    use_rust_library,
)
from pyet_mc.pyet_utils import Trace

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_synthetic_data(seed=42):
    """Create reproducible synthetic decay data for fitting tests."""
    rng = np.random.default_rng(seed)
    time = np.linspace(0.01, 10, 200)
    # Fake radial data (100 distance samples)
    radial_data = rng.uniform(0.5, 5.0, size=100)
    true_params = {"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01}
    y_clean = general_energy_transfer(time, radial_data, true_params)
    noise = 0.005 * rng.normal(size=time.size)
    y_noisy = y_clean + noise
    return time, radial_data, y_noisy, true_params


# ---------------------------------------------------------------------------
# general_energy_transfer
# ---------------------------------------------------------------------------


class TestGeneralEnergyTransfer(unittest.TestCase):
    """Tests for the Python general_energy_transfer model."""

    def test_basic_output_shape(self):
        time = np.linspace(0, 10, 50)
        radial = np.array([1.0, 2.0, 3.0])
        params = {"amp": 1.0, "cr": 10.0, "rad": 0.1, "offset": 0.0}
        result = general_energy_transfer(time, radial, params)
        self.assertEqual(result.shape, time.shape)

    def test_zero_time_gives_amplitude(self):
        """At t=0 the exponentials are all 1, so result ≈ amp + offset."""
        time = np.array([0.0])
        radial = np.array([1.0, 2.0, 3.0])
        params = {"amp": 2.0, "cr": 100.0, "rad": 5.0, "offset": 0.5}
        result = general_energy_transfer(time, radial, params)
        np.testing.assert_allclose(result, [2.0 + 0.5], atol=1e-12)

    def test_offset_shifts_baseline(self):
        time = np.linspace(0, 10, 20)
        radial = np.array([1.0, 2.0])
        params_no_offset = {"amp": 1.0, "cr": 5.0, "rad": 0.1, "offset": 0.0}
        params_with_offset = {"amp": 1.0, "cr": 5.0, "rad": 0.1, "offset": 0.3}
        r1 = general_energy_transfer(time, radial, params_no_offset)
        r2 = general_energy_transfer(time, radial, params_with_offset)
        np.testing.assert_allclose(r2 - r1, 0.3, atol=1e-12)

    def test_too_few_values_raises(self):
        """Passing fewer than 4 values should raise an IndexError."""
        time = np.linspace(0, 1, 5)
        radial = np.array([1.0])
        bad_params = {"a": 1, "b": 2}
        with self.assertRaises(IndexError):
            general_energy_transfer(time, radial, bad_params)

    def test_large_time_decays_to_offset(self):
        """At very large t, all exponentials → 0 so result → offset."""
        time = np.array([1e6])
        radial = np.array([1.0, 2.0, 3.0])
        params = {"amp": 5.0, "cr": 1.0, "rad": 0.1, "offset": 0.42}
        result = general_energy_transfer(time, radial, params)
        np.testing.assert_allclose(result, [0.42], atol=1e-12)


# ---------------------------------------------------------------------------
# double_exp
# ---------------------------------------------------------------------------


class TestDoubleExp(unittest.TestCase):
    """Tests for the double_exp model function."""

    def test_basic_shape(self):
        time = np.linspace(0, 5, 30)
        params = {"amp": 2.0, "p": 1.0, "q": 3.0}
        result = double_exp(time, params)
        self.assertEqual(result.shape, time.shape)

    def test_zero_time(self):
        """At t=0: amp*(1-1) = 0."""
        time = np.array([0.0])
        params = {"amp": 5.0, "p": 1.0, "q": 2.0}
        result = double_exp(time, params)
        np.testing.assert_allclose(result, [0.0], atol=1e-12)

    def test_too_few_values_raises(self):
        """Passing fewer than 3 values should raise an IndexError."""
        time = np.array([1.0])
        bad_params = {"A": 1}
        with self.assertRaises(IndexError):
            double_exp(time, bad_params)

    def test_known_value(self):
        """Verify against hand-calculated value."""
        time = np.array([1.0])
        params = {"amp": 1.0, "p": 0.5, "q": 2.0}
        expected = 1.0 * (np.exp(-0.5) - np.exp(-2.0))
        result = double_exp(time, params)
        np.testing.assert_allclose(result, [expected], atol=1e-12)


# ---------------------------------------------------------------------------
# Rust wrappers (only run if Rust bindings are available)
# ---------------------------------------------------------------------------


@unittest.skipUnless(use_rust_library, "Rust bindings not available")
class TestRustWrappers(unittest.TestCase):
    """Verify that Rust wrappers produce identical results to the Python model."""

    def setUp(self):
        from pyet_mc.fitting import _rust_energy_transfer, _rust_energy_transfer_para

        self._rust_seq = _rust_energy_transfer
        self._rust_par = _rust_energy_transfer_para

    def test_sequential_matches_python(self):
        time = np.linspace(0.01, 10, 100)
        radial = np.array([0.5, 1.0, 2.0, 3.5])
        params = {"amp": 1.5, "cr": 20.0, "rad": 0.3, "offset": 0.05}
        py_result = general_energy_transfer(time, radial, params)
        rs_result = self._rust_seq(time, radial, params)
        np.testing.assert_allclose(rs_result, py_result, rtol=1e-10)

    def test_parallel_matches_python(self):
        time = np.linspace(0.01, 10, 100)
        radial = np.array([0.5, 1.0, 2.0, 3.5])
        params = {"amp": 1.5, "cr": 20.0, "rad": 0.3, "offset": 0.05}
        py_result = general_energy_transfer(time, radial, params)
        rs_result = self._rust_par(time, radial, params)
        np.testing.assert_allclose(rs_result, py_result, rtol=1e-10)

    def test_sequential_matches_parallel(self):
        time = np.linspace(0, 5, 200)
        radial = np.random.default_rng(7).uniform(0.1, 4.0, size=50)
        params = {"amp": 2.0, "cr": 100.0, "rad": 1.0, "offset": 0.0}
        seq = self._rust_seq(time, radial, params)
        par = self._rust_par(time, radial, params)
        np.testing.assert_allclose(seq, par, rtol=1e-12)

    def test_wrapper_returns_numpy_array(self):
        time = np.array([0.0, 1.0])
        radial = np.array([1.0])
        params = {"amp": 1.0, "cr": 1.0, "rad": 0.1, "offset": 0.0}
        self.assertIsInstance(self._rust_seq(time, radial, params), np.ndarray)
        self.assertIsInstance(self._rust_par(time, radial, params), np.ndarray)


# ---------------------------------------------------------------------------
# Optimiser construction
# ---------------------------------------------------------------------------


class TestOptimiserInit(unittest.TestCase):
    """Test Optimiser initialisation, model selection, and weight adjustment."""

    def _make_trace(self, n=50, name="test"):
        rng = np.random.default_rng(0)
        return Trace(
            ydata=rng.random(n),
            xdata=np.linspace(0, 5, n),
            fname=name,
            radial_data=rng.uniform(0.5, 3.0, 20),
        )

    def test_default_model(self):
        t = self._make_trace()
        opt = Optimiser([t], [["amp", "cr", "rad", "offset"]], auto_weights=False)
        self.assertIs(opt.model, general_energy_transfer)

    @unittest.skipUnless(use_rust_library, "Rust bindings not available")
    def test_rs_model(self):
        from pyet_mc.fitting import _rust_energy_transfer_para

        t = self._make_trace()
        opt = Optimiser(
            [t], [["amp", "cr", "rad", "offset"]], auto_weights=False, model="rs"
        )
        self.assertIs(opt.model, _rust_energy_transfer_para)

    @unittest.skipUnless(use_rust_library, "Rust bindings not available")
    def test_rs_single_model(self):
        from pyet_mc.fitting import _rust_energy_transfer

        t = self._make_trace()
        opt = Optimiser(
            [t], [["amp", "cr", "rad", "offset"]], auto_weights=False, model="rs_single"
        )
        self.assertIs(opt.model, _rust_energy_transfer)

    def test_custom_callable_model(self):
        def my_model(time, radial, d):
            return np.ones_like(time) * d.get("val", 0)

        t = self._make_trace()
        opt = Optimiser([t], [["val"]], auto_weights=False, model=my_model)
        self.assertIs(opt.model, my_model)

    def test_auto_weights_adjusts(self):
        t1 = self._make_trace(n=100, name="long")
        t2 = self._make_trace(n=50, name="short")
        # auto_weights=True by default
        opt = Optimiser([t1, t2], [["amp", "cr", "rad", "offset"]] * 2)
        # The shorter trace should have a higher weight
        self.assertGreater(t2.weight, t1.weight)


# ---------------------------------------------------------------------------
# wrss (single code path)
# ---------------------------------------------------------------------------


class TestWrss(unittest.TestCase):
    """Test that wrss computes correctly with the unified code path."""

    def test_wrss_zero_residuals(self):
        """If model output matches trace data exactly, wrss should be 0."""
        time = np.linspace(0.01, 5, 50)
        radial = np.array([1.0, 2.0])
        params = {"amp": 1.0, "cr": 10.0, "rad": 0.2, "offset": 0.0}
        y = general_energy_transfer(time, radial, params)
        t = Trace(y, time, "perfect", radial)
        opt = Optimiser([t], [["amp", "cr", "rad", "offset"]], auto_weights=False)
        wrss_val = opt.wrss(params)
        self.assertAlmostEqual(wrss_val, 0.0, places=10)

    def test_wrss_positive_for_bad_params(self):
        time = np.linspace(0.01, 5, 50)
        radial = np.array([1.0, 2.0])
        true_params = {"amp": 1.0, "cr": 10.0, "rad": 0.2, "offset": 0.0}
        y = general_energy_transfer(time, radial, true_params)
        t = Trace(y, time, "data", radial)
        opt = Optimiser([t], [["amp", "cr", "rad", "offset"]], auto_weights=False)
        bad_params = {"amp": 2.0, "cr": 5.0, "rad": 1.0, "offset": 0.5}
        self.assertGreater(opt.wrss(bad_params), 0)

    def test_wrss_custom_model(self):
        """wrss works with a custom model via the single code path."""

        def constant_model(time, radial, d):
            return np.full_like(time, d["c"])

        time = np.linspace(0, 1, 20)
        radial = np.array([1.0])
        y = np.full(20, 3.0)
        t = Trace(y, time, "const", radial)
        opt = Optimiser([t], [["c"]], auto_weights=False, model=constant_model)
        # Perfect match
        self.assertAlmostEqual(opt.wrss({"c": 3.0}), 0.0, places=10)
        # Off by 1
        expected = 20 * 1.0**2  # weight=1, 20 points, each residual=1
        self.assertAlmostEqual(opt.wrss({"c": 4.0}), expected, places=10)

    @unittest.skipUnless(use_rust_library, "Rust bindings not available")
    def test_wrss_rust_model_same_as_python(self):
        """Rust and Python models should give identical wrss for the same params."""
        time = np.linspace(0.01, 5, 80)
        radial = np.random.default_rng(99).uniform(0.5, 3.0, 30)
        params = {"amp": 1.0, "cr": 20.0, "rad": 0.3, "offset": 0.02}
        y = general_energy_transfer(time, radial, params)
        t = Trace(y, time, "data", radial)

        opt_py = Optimiser(
            [t], [["amp", "cr", "rad", "offset"]], auto_weights=False, model="default"
        )
        opt_rs = Optimiser(
            [t], [["amp", "cr", "rad", "offset"]], auto_weights=False, model="rs"
        )

        test_params = {"amp": 1.1, "cr": 18.0, "rad": 0.35, "offset": 0.01}
        np.testing.assert_allclose(
            opt_py.wrss(test_params), opt_rs.wrss(test_params), rtol=1e-8
        )


# ---------------------------------------------------------------------------
# _run_solver / fit
# ---------------------------------------------------------------------------


class TestSolverDispatch(unittest.TestCase):
    """Test that _run_solver dispatches correctly and wraps result.x as a dict."""

    def setUp(self):
        self.time, self.radial, self.y, self.true_params = _make_synthetic_data()
        self.trace = Trace(self.y, self.time, "synth", self.radial)
        self.variables = [["amp", "cr", "rad", "offset"]]

    def test_unsupported_solver_raises(self):
        opt = Optimiser([self.trace], self.variables, auto_weights=False)
        with self.assertRaises(ValueError) as ctx:
            opt.fit(
                guess={"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01},
                solver="nonexistent_solver",
            )
        self.assertIn("Unsupported solver", str(ctx.exception))

    @patch("pyet_mc.fitting.fit_logger")
    def test_minimize_returns_dict_x(self, mock_logger):
        opt = Optimiser([self.trace], self.variables, auto_weights=False)
        result = opt.fit(
            guess={"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01},
            solver="minimize",
            method="Nelder-Mead",
            options={"maxiter": 50},
        )
        self.assertIsInstance(result, scipy.optimize.OptimizeResult)
        self.assertIsInstance(result.x, dict)
        self.assertSetEqual(set(result.x.keys()), {"amp", "cr", "rad", "offset"})

    @patch("pyet_mc.fitting.fit_logger")
    def test_minimize_recovers_params(self, mock_logger):
        """With enough iterations the fit should recover reasonable params."""
        opt = Optimiser([self.trace], self.variables, auto_weights=False)
        result = opt.fit(
            guess={"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01},
            solver="minimize",
            method="Nelder-Mead",
            tol=1e-14,
        )
        # Check the optimiser converged (wrss should be small)
        self.assertLess(result.fun, 1.0)
        # result.x should be a dict with all expected keys
        self.assertSetEqual(set(result.x.keys()), {"amp", "cr", "rad", "offset"})

    @patch("pyet_mc.fitting.fit_logger")
    def test_differential_evolution(self, mock_logger):
        opt = Optimiser([self.trace], self.variables, auto_weights=False)
        bounds = {
            "amp": (0.5, 2.0),
            "cr": (10.0, 200.0),
            "rad": (0.01, 1.0),
            "offset": (-0.1, 0.1),
        }
        result = opt.fit(
            guess={"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01},
            bounds=bounds,
            solver="differential_evolution",
            maxiter=10,
            seed=42,
            tol=0.1,
        )
        self.assertIsInstance(result.x, dict)
        self.assertSetEqual(set(result.x.keys()), {"amp", "cr", "rad", "offset"})

    @patch("pyet_mc.fitting.fit_logger")
    def test_dual_annealing(self, mock_logger):
        opt = Optimiser([self.trace], self.variables, auto_weights=False)
        bounds = {
            "amp": (0.5, 2.0),
            "cr": (10.0, 200.0),
            "rad": (0.01, 1.0),
            "offset": (-0.1, 0.1),
        }
        result = opt.fit(
            guess={"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01},
            bounds=bounds,
            solver="dual_annealing",
            maxiter=10,
            seed=42,
        )
        self.assertIsInstance(result.x, dict)

    @patch("pyet_mc.fitting.fit_logger")
    def test_basinhopping(self, mock_logger):
        opt = Optimiser([self.trace], self.variables, auto_weights=False)
        result = opt.fit(
            guess={"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01},
            solver="basinhopping",
            niter=2,
            minimizer_kwargs={"method": "Nelder-Mead", "options": {"maxiter": 50}},
        )
        self.assertIsInstance(result.x, dict)


# ---------------------------------------------------------------------------
# Multi-trace / shared parameter fitting
# ---------------------------------------------------------------------------


class TestMultiTraceFit(unittest.TestCase):
    """Test coupled fitting across multiple traces with shared parameters.

    The built-in general_energy_transfer uses positional dict access, so
    per-trace variable names (amp1, cr, rad, offset1) work directly — the
    key names are irrelevant, only the insertion order matters.
    """

    @patch("pyet_mc.fitting.fit_logger")
    def test_shared_params_are_identical(self, mock_logger):
        """When two traces share 'cr' and 'rad', the fit should return a single value for each."""
        rng = np.random.default_rng(123)
        time = np.linspace(0.01, 8, 100)
        radial1 = rng.uniform(0.5, 4.0, 40)
        radial2 = rng.uniform(0.5, 4.0, 60)

        true = {"amp": 1.0, "cr": 30.0, "rad": 0.15, "offset": 0.0}
        y1 = general_energy_transfer(time, radial1, true) + 0.005 * rng.normal(
            size=time.size
        )
        y2 = general_energy_transfer(time, radial2, true) + 0.005 * rng.normal(
            size=time.size
        )

        t1 = Trace(y1, time, "trace1", radial1)
        t2 = Trace(y2, time, "trace2", radial2)

        vars1 = ["amp1", "cr", "rad", "offset1"]
        vars2 = ["amp2", "cr", "rad", "offset2"]

        opt = Optimiser([t1, t2], [vars1, vars2], auto_weights=False)
        result = opt.fit(
            guess={
                "amp1": 0.9,
                "amp2": 0.9,
                "cr": 25.0,
                "rad": 0.1,
                "offset1": 0.0,
                "offset2": 0.0,
            },
            solver="minimize",
            method="Nelder-Mead",
            tol=1e-12,
        )
        # Shared params should exist once in the result
        self.assertIn("cr", result.x)
        self.assertIn("rad", result.x)
        # Both amp values should be close to 1.0
        self.assertAlmostEqual(result.x["amp1"], 1.0, delta=0.5)
        self.assertAlmostEqual(result.x["amp2"], 1.0, delta=0.5)


# ---------------------------------------------------------------------------
# Uncertainties
# ---------------------------------------------------------------------------


class TestUncertainties(unittest.TestCase):
    @patch("pyet_mc.fitting.fit_logger")
    def test_uncertainties_populated(self, mock_logger):
        """After a fit, self.uncertainty should have the same keys as result.x."""
        time, radial, y, true_params = _make_synthetic_data()
        trace = Trace(y, time, "test", radial)
        opt = Optimiser([trace], [["amp", "cr", "rad", "offset"]], auto_weights=False)
        result = opt.fit(
            guess={"amp": 1.0, "cr": 50.0, "rad": 0.2, "offset": 0.01},
            solver="minimize",
            method="Nelder-Mead",
            options={"maxiter": 100},
        )
        self.assertIsInstance(opt.uncertainty, dict)
        self.assertSetEqual(set(opt.uncertainty.keys()), set(result.x.keys()))
        for v in opt.uncertainty.values():
            self.assertIsInstance(v, float)


if __name__ == "__main__":
    unittest.main()
