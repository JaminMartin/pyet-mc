import os
import unittest
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from pyet_mc.structure import Structure


class TestClass(unittest.TestCase):
    def setUp(self):

        # Path to a CIF file for testing
        cif_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "src", "cif_files")
        )
        cif_file = os.path.join(cif_dir, "KY3F10_mp-2943_conventional_standard.cif")
        # Create an instance of Structure with the dummy CIF file

        self.obj = Structure(cif_file)
        self.obj.centre_ion("Y")

    def test_nearest_neighbours_coords(self):
        # Call the method with a test radius
        result = self.obj.nearest_neighbours_coords(5.0)
        # Check that the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        # Check that the DataFrame has the expected columns
        self.assertListEqual(list(result.columns), ["x", "y", "z", "species"])

    def test_nearest_neighbours_spherical_coords(self):
        # Call the method with a test radius

        result = self.obj.nearest_neighbours_spherical_coords(5.0)
        # Check that the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        # Check that the DataFrame has the expected columns
        self.assertListEqual(list(result.columns), ["r", "theta", "phi", "species"])

    def test_structure_plot(self):
        # Call the method with a test radius and filter
        try:
            self.obj.structure_plot(5.0, filter=["F", "K"])
        except Exception as e:
            self.fail(f"structure_plot raised Exception unexpectedly: {e}")

    def test_structure_plot_invalid_inputs_radius(self):
        # Call the method with invalid inputs — a string radius causes a TypeError
        # from the underlying pymatgen get_neighbors call
        with self.assertRaises((ValueError, TypeError)):
            self.obj.structure_plot("invalid_radius", filter=["F", "K"])

    def test_structure_plot_invalid_inputs_filter(self):
        # Call the method with invalid inputs and assert that it raises a value error e.g. when the radius is not given as a float/int
        with self.assertRaises(TypeError):  #
            self.obj.structure_plot(5.0, filter="F")
        with self.assertRaises(TypeError):  #
            self.obj.structure_plot(5.0, filter=[5, 5, 5])
        with self.assertRaises(KeyError):  #
            self.obj.structure_plot(5.0, filter=["R", "F"])


if __name__ == "__main__":
    unittest.main()
