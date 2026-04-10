"""Tests for pyet_mc.pyet_utils — Trace class and utility functions."""

import json
import os
import shutil
import tempfile
import unittest

import numpy as np
import pandas as pd

from pyet_mc.pyet_utils import (
    Gamma2sigma,
    Trace,
    cache_clear,
    cache_list,
    cache_reader,
    cache_writer,
    name_checker,
)


class TestTrace(unittest.TestCase):
    """Tests for the Trace data container."""

    def setUp(self):
        self.time = np.linspace(0, 10, 1000)
        self.ydata = np.exp(-0.5 * self.time)
        self.radial = np.random.default_rng(42).random(50)
        self.name = "test_trace"

    def test_basic_construction(self):
        """Trace stores time, ydata, name, radial_data and default weight."""
        t = Trace(self.ydata, self.time, self.name, self.radial)
        np.testing.assert_array_equal(t.trace, self.ydata)
        np.testing.assert_array_equal(t.time, self.time)
        np.testing.assert_array_equal(t.radial_data, self.radial)
        self.assertEqual(t.name, self.name)
        self.assertEqual(t.weight, 1)
        self.assertEqual(t.parser, "None")

    def test_custom_weight(self):
        """Custom weighting is stored."""
        t = Trace(self.ydata, self.time, self.name, self.radial, weighting=3)
        self.assertEqual(t.weight, 3)

    def test_parse_10(self):
        """parse_10 keeps every 10th data point."""
        t = Trace(self.ydata, self.time, self.name, self.radial, parser="parse_10")
        self.assertEqual(t.parser, "parse_10")
        self.assertEqual(len(t.trace), 100)  # 1000 / 10
        self.assertEqual(len(t.time), 100)

    def test_parse_100(self):
        """parse_100 keeps every 100th data point."""
        t = Trace(self.ydata, self.time, self.name, self.radial, parser="parse_100")
        self.assertEqual(t.parser, "parse_100")
        self.assertEqual(len(t.trace), 10)  # 1000 / 100
        self.assertEqual(len(t.time), 10)

    def test_parse_log(self):
        """parse_log produces logarithmically-spaced indices (≤500 unique points)."""
        t = Trace(self.ydata, self.time, self.name, self.radial, parser="parse_log")
        self.assertEqual(t.parser, "parse_log")
        self.assertLessEqual(len(t.trace), 500)
        self.assertGreater(len(t.trace), 0)
        self.assertEqual(len(t.trace), len(t.time))

    def test_invalid_parser(self):
        """An unrecognised parser string triggers an UnboundLocalError (known bug in Trace).

        The match/case _: branch prints a message but never assigns `indices`,
        so the subsequent `self.trace = self.trace[indices]` crashes.
        We verify the current (buggy) behaviour so CI catches it if/when it's fixed.
        """
        with self.assertRaises(UnboundLocalError):
            Trace(self.ydata, self.time, self.name, self.radial, parser="nonexistent")

    def test_parse_preserves_correspondence(self):
        """After parsing, time[i] still corresponds to trace[i]."""
        t = Trace(self.ydata, self.time, self.name, self.radial, parser="parse_10")
        # The original data is y = exp(-0.5 * x), so check a few points
        for i in range(len(t.time)):
            expected = np.exp(-0.5 * t.time[i])
            np.testing.assert_almost_equal(t.trace[i], expected, decimal=10)


class TestGamma2sigma(unittest.TestCase):
    """Tests for the Gamma2sigma helper."""

    def test_known_conversion(self):
        """Gamma2sigma uses: sigma = Gamma * sqrt(2) / (2 * sqrt(2*ln(2))).

        For Gamma = 2*sqrt(2*ln(2)) ≈ 2.3548, the result is sqrt(2) ≈ 1.4142.
        """
        fwhm = 2.3548200450309493
        sigma = Gamma2sigma(fwhm)
        expected = np.sqrt(2)
        self.assertAlmostEqual(sigma, expected, places=5)

    def test_zero(self):
        """Zero linewidth gives zero sigma."""
        self.assertAlmostEqual(Gamma2sigma(0), 0.0)


class TestNameChecker(unittest.TestCase):
    """Tests for the name_checker utility."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_returns_filename_when_no_conflict(self):
        """When no file exists at the path, the filename is returned as-is."""
        path = os.path.join(self.tmpdir, "0-fitlog.pyet")
        result = name_checker(path)
        self.assertEqual(result, "0-fitlog.pyet")

    def test_increments_on_conflict(self):
        """When the file already exists, the prefix number is incremented."""
        path = os.path.join(self.tmpdir, "0-fitlog.pyet")
        # Create the file so there's a conflict
        with open(path, "w") as f:
            f.write("existing")
        result = name_checker(path)
        self.assertIn("1-fitlog.pyet", result)


class TestCacheRoundTrip(unittest.TestCase):
    """Tests for cache_writer and cache_reader."""

    def setUp(self):
        # Point the cache directory to a temp location
        self.original_cache = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "src", "pyet_mc", "cache")
        )
        self.test_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    def test_writer_creates_file(self):
        """cache_writer should create a JSON file in the cache directory."""
        # This uses the real cache dir — write a uniquely-named entry
        cache_writer(
            self.test_data,
            sourcefile="test_roundtrip.cif",
            process="singlecross",
            radius=5,
            concentration=99.99,
            iterations=3,
            interaction_type="DD",
            intrinsic=False,
        )
        # Verify we can read it back
        result = cache_reader(
            sourcefile="test_roundtrip.cif",
            process="singlecross",
            radius=5,
            concentration=99.99,
            iterations=3,
            interaction_type="DD",
            intrinsic=False,
        )
        self.assertIsNotNone(result)
        np.testing.assert_array_almost_equal(result, self.test_data)

        # Clean up the cache file we created
        cache_dir = self.original_cache
        for f in os.listdir(cache_dir):
            if "test_roundtrip" in f and f.endswith(".json"):
                os.remove(os.path.join(cache_dir, f))

    def test_reader_returns_none_for_missing(self):
        """cache_reader returns None when no matching cache file exists."""
        result = cache_reader(
            sourcefile="nonexistent_structure.cif",
            process="singlecross",
            radius=999,
            concentration=0.001,
            iterations=1,
            interaction_type="DD",
            intrinsic=False,
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
