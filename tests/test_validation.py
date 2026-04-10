"""
Tests for input validation in Structure, Interaction, and related classes.

These tests verify that proper errors are raised for invalid inputs,
missing prerequisites, and edge cases.
"""

import os
import unittest

import numpy as np
import pandas as pd

from pyet_mc.structure import Interaction, Structure


def _cif_path():
    """Return the path to the test CIF file."""
    cif_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src", "cif_files")
    )
    return os.path.join(cif_dir, "KY3F10_mp-2943_conventional_standard.cif")


class TestStructureValidation(unittest.TestCase):
    """Tests for Structure.__init__ and centre_ion validation."""

    def test_init_missing_file_raises_file_not_found(self):
        """Structure() with a nonexistent path must raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            Structure("this_file_does_not_exist.cif")

    def test_init_missing_file_message_contains_path(self):
        """The FileNotFoundError message should include the bad path."""
        bad_path = "/tmp/nonexistent_abc123.cif"
        with self.assertRaises(FileNotFoundError) as ctx:
            Structure(bad_path)
        self.assertIn(bad_path, str(ctx.exception))

    def test_init_valid_cif(self):
        """Structure() with a valid CIF file should succeed."""
        cif_file = _cif_path()
        if not os.path.isfile(cif_file):
            self.skipTest(f"CIF file not available: {cif_file}")
        s = Structure(cif_file)
        self.assertTrue(hasattr(s, "struct"))
        self.assertTrue(hasattr(s, "cif"))

    def test_centre_ion_valid(self):
        """centre_ion with a valid species should set attributes."""
        cif_file = _cif_path()
        if not os.path.isfile(cif_file):
            self.skipTest(f"CIF file not available: {cif_file}")
        s = Structure(cif_file)
        # Y is a species in KY3F10
        s.centre_ion("Y")
        self.assertTrue(hasattr(s, "ion_index"))
        self.assertTrue(hasattr(s, "site"))
        self.assertTrue(hasattr(s, "centre_ion_species"))
        self.assertTrue(hasattr(s, "origin"))
        self.assertEqual(s.centre_ion_species, "Y")

    def test_centre_ion_not_found_raises_value_error(self):
        """centre_ion with a species not in the structure must raise ValueError."""
        cif_file = _cif_path()
        if not os.path.isfile(cif_file):
            self.skipTest(f"CIF file not available: {cif_file}")
        s = Structure(cif_file)
        with self.assertRaises(ValueError) as ctx:
            s.centre_ion("Zz")  # nonsense species
        self.assertIn("not found", str(ctx.exception))
        self.assertIn("Available species", str(ctx.exception))

    def test_centre_ion_error_lists_available_species(self):
        """The ValueError from centre_ion should list what species are available."""
        cif_file = _cif_path()
        if not os.path.isfile(cif_file):
            self.skipTest(f"CIF file not available: {cif_file}")
        s = Structure(cif_file)
        with self.assertRaises(ValueError) as ctx:
            s.centre_ion("Unobtainium")
        msg = str(ctx.exception)
        # KY3F10 has F, K, Y
        self.assertIn("F", msg)
        self.assertIn("K", msg)
        self.assertIn("Y", msg)


class TestInteractionValidation(unittest.TestCase):
    """Tests for Interaction input validation: doper() without distance_sim()."""

    def _make_interaction(self):
        """Helper to create a valid Interaction object."""
        cif_file = _cif_path()
        if not os.path.isfile(cif_file):
            self.skipTest(f"CIF file not available: {cif_file}")
        s = Structure(cif_file)
        s.centre_ion("Y")
        return Interaction(s)

    def test_doper_without_distance_sim_raises_attribute_error(self):
        """Calling doper() before distance_sim() must raise AttributeError."""
        interaction = self._make_interaction()
        with self.assertRaises(AttributeError) as ctx:
            interaction.doper(concentration=15, dopant="Sm")
        self.assertIn("distance_sim", str(ctx.exception))

    def test_doper_after_distance_sim_succeeds(self):
        """Calling doper() after distance_sim() should work normally."""
        interaction = self._make_interaction()
        interaction.distance_sim(radius=10)
        result = interaction.doper(concentration=15, dopant="Sm")
        self.assertIsInstance(result, np.ndarray)

    def test_doper_return_coords(self):
        """doper(return_coords=True) should return a DataFrame."""
        interaction = self._make_interaction()
        interaction.distance_sim(radius=10)
        result = interaction.doper(concentration=15, dopant="Sm", return_coords=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("r", result.columns)
        self.assertIn("species", result.columns)

    def test_doper_does_not_mutate_filtered_coords(self):
        """doper() should reset filtered_coords after each call."""
        interaction = self._make_interaction()
        interaction.distance_sim(radius=10)
        original = interaction.filtered_coords.copy()
        interaction.doper(concentration=50, dopant="Sm")
        pd.testing.assert_frame_equal(interaction.filtered_coords, original)

    def test_distance_sim_populates_filtered_coords(self):
        """distance_sim() should populate filtered_coords as a DataFrame."""
        interaction = self._make_interaction()
        interaction.distance_sim(radius=10)
        self.assertTrue(hasattr(interaction, "filtered_coords"))
        self.assertIsInstance(interaction.filtered_coords, pd.DataFrame)
        self.assertGreater(len(interaction.filtered_coords), 0)


class TestStructureNeighbours(unittest.TestCase):
    """Tests for nearest neighbour queries."""

    def setUp(self):
        cif_file = _cif_path()
        if not os.path.isfile(cif_file):
            self.skipTest(f"CIF file not available: {cif_file}")
        self.s = Structure(cif_file)
        self.s.centre_ion("Y")

    def test_nearest_neighbours_coords_returns_dataframe(self):
        result = self.s.nearest_neighbours_coords(5.0)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertListEqual(list(result.columns), ["x", "y", "z", "species"])

    def test_nearest_neighbours_spherical_coords_returns_dataframe(self):
        result = self.s.nearest_neighbours_spherical_coords(5.0)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertListEqual(list(result.columns), ["r", "theta", "phi", "species"])

    def test_nearest_neighbours_coords_small_radius_may_be_empty(self):
        """A very small radius might return an empty DataFrame."""
        result = self.s.nearest_neighbours_coords(0.01)
        self.assertIsInstance(result, pd.DataFrame)

    def test_nearest_neighbours_large_radius_has_results(self):
        """A large radius should find many neighbours."""
        result = self.s.nearest_neighbours_coords(10.0)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
