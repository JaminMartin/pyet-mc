"""Tests for pyet_mc top-level public API re-exports."""

import unittest


class TestPublicAPI(unittest.TestCase):
    """Verify that all advertised symbols are importable from the top-level package."""

    def test_import_structure(self):
        from pyet_mc import Structure

        self.assertTrue(callable(Structure))

    def test_import_interaction(self):
        from pyet_mc import Interaction

        self.assertTrue(callable(Interaction))

    def test_import_optimiser(self):
        from pyet_mc import Optimiser

        self.assertTrue(callable(Optimiser))

    def test_import_trace(self):
        from pyet_mc import Trace

        self.assertTrue(callable(Trace))

    def test_import_plot(self):
        from pyet_mc import Plot

        self.assertTrue(callable(Plot))

    def test_import_general_energy_transfer(self):
        from pyet_mc import general_energy_transfer

        self.assertTrue(callable(general_energy_transfer))

    def test_import_double_exp(self):
        from pyet_mc import double_exp

        self.assertTrue(callable(double_exp))

    def test_all_contains_expected_names(self):
        import pyet_mc

        expected = {
            "Structure",
            "Interaction",
            "Optimiser",
            "Trace",
            "Plot",
            "general_energy_transfer",
            "double_exp",
        }
        self.assertTrue(
            expected.issubset(set(pyet_mc.__all__)),
            f"Missing from __all__: {expected - set(pyet_mc.__all__)}",
        )

    def test_submodule_imports_still_work(self):
        """Ensure the old explicit import paths haven't been broken."""
        from pyet_mc.fitting import Optimiser, double_exp, general_energy_transfer
        from pyet_mc.plotting import Plot
        from pyet_mc.pyet_utils import Trace
        from pyet_mc.structure import Interaction, Structure

        for cls in (Structure, Interaction, Optimiser, Trace, Plot):
            self.assertTrue(callable(cls))
        for fn in (general_energy_transfer, double_exp):
            self.assertTrue(callable(fn))


if __name__ == "__main__":
    unittest.main()
