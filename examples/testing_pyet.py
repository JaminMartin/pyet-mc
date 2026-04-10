"""
testing_pyet.py

A complete example demonstrating the pyet-mc workflow:
1. Loading a crystal structure from a CIF file
2. Querying nearest neighbour information
3. Plotting the crystal structure (full and filtered)
4. Using the two-step distance_sim() + doper() workflow
5. Plotting a doped crystal structure
6. Running Monte Carlo interaction simulations via sim_single_cross()
7. Generating synthetic decay data
8. Fitting the data using the Optimiser
9. Plotting the fitted results
"""

import numpy as np

from pyet_mc.fitting import Optimiser, general_energy_transfer
from pyet_mc.plotting import Plot
from pyet_mc.pyet_utils import Trace
from pyet_mc.structure import Interaction, Structure

if __name__ == "__main__":
    # =========================================================================
    # 1. Load the crystal structure from a CIF file
    # =========================================================================
    # The CIF file should use the conventional standard.
    # CIF files can be obtained from the Materials Project:
    # https://next-gen.materialsproject.org/api
    KY3F10 = Structure(cif_file="KY3F10.cif")

    # =========================================================================
    # 2. Specify a central ion and query nearest neighbours
    # =========================================================================
    # The charge must be specified (e.g. 'Y3+', not 'Y')
    KY3F10.centre_ion("Y3+")

    # Print nearest neighbour info within 3.2 Angstroms of the central Y3+ ion
    KY3F10.nearest_neighbours_info(3.2)

    # =========================================================================
    # 3. Plot the crystal structure
    # =========================================================================
    # Full structure plot within a 5 Angstrom radius
    fig1 = KY3F10.structure_plot(radius=5)
    fig1.show()

    # Filtered plot showing only specific species (charge must be specified!)
    filtered_ions = ["F-", "K+"]
    fig2 = KY3F10.structure_plot(radius=5, filter=filtered_ions)
    fig2.show()

    # =========================================================================
    # 4. Demonstrate the two-step distance_sim() + doper() workflow
    # =========================================================================
    # Create an Interaction object from our structure
    crystal_interaction = Interaction(KY3F10)

    # Step 1: Compute spherical coordinates of all same-species (Y3+) ions
    # within a 10 Angstrom radius. This populates crystal_interaction.filtered_coords
    # with the candidate sites that *could* be doped — they are all Y3+ at this stage.
    crystal_interaction.distance_sim(radius=10)

    print("Candidate sites (all same-species Y3+ ions within radius):")
    print(crystal_interaction.filtered_coords)
    print()

    # Step 2: Randomly assign dopant species based on concentration (in %)
    # and retrieve the radial distances of the resulting dopant ions.
    # doper() temporarily replaces a random subset of the Y3+ sites with Sm3+
    # (based on the 15% concentration), extracts the Sm3+ distances, and then
    # resets filtered_coords back to the original Y3+ sites. This means
    # filtered_coords is unchanged after calling doper() — only the returned
    # result contains the doped configuration.

    # Default: returns just the radial distances as a numpy array
    distances = crystal_interaction.doper(concentration=15, dopant="Sm3+")
    print(f"Radial distances (Angstroms) of {len(distances)} dopant Sm3+ ions:")
    print(distances)
    print()

    # With return_coords=True: returns the full doped configuration as a
    # DataFrame with r, theta, phi, and species — useful for inspecting which
    # sites were randomly assigned as dopants.
    doped_config = crystal_interaction.doper(
        concentration=15, dopant="Sm3+", return_coords=True
    )
    print("Full doped configuration (Y3+ = undoped, Sm3+ = doped):")
    print(doped_config)
    print()

    # Each call to doper() produces a different random configuration — this is
    # the basis of the Monte Carlo approach. sim_single_cross() calls
    # distance_sim() once, then doper() for each iteration internally, so you
    # do not need to call them separately when using it. The two-step workflow
    # above is useful when building custom interaction models.

    # =========================================================================
    # 5. Plot a doped crystal structure
    # =========================================================================
    fig3 = crystal_interaction.doped_structure_plot(
        radius=7.0, concentration=15.0, dopant="Sm3+", filter=["Y3+", "Sm3+"]
    )
    fig3.show()

    # =========================================================================
    # 6. Run Monte Carlo interaction simulations
    # =========================================================================
    # sim_single_cross handles the full Monte Carlo workflow internally:
    # it calls distance_sim() once, then doper() for each iteration.
    # Interaction type codes: 'DD' = dipole-dipole, 'DQ' = dipole-quadrupole,
    # 'QQ' = quadrupole-quadrupole
    interaction_components2pt5pct = crystal_interaction.sim_single_cross(
        radius=10, concentration=2.5, interaction_type="DQ", iterations=1000
    )
    interaction_components5pct = crystal_interaction.sim_single_cross(
        radius=10, concentration=5.0, interaction_type="DQ", iterations=1000
    )

    # =========================================================================
    # 7. Generate synthetic decay data
    # =========================================================================
    # Specify physical constants (time-based constants are in ms^-1)
    # The general_energy_transfer function accesses values by position (insertion order):
    # [0] amplitude, [1] energy_transfer_rate, [2] radiative_decay_rate, [3] offset
    const_dict1 = {
        "amp": 1,
        "cr": 500,
        "rad": 0.144,
        "offset": 0,
    }
    const_dict2 = {
        "amp": 1,
        "cr": 500,
        "rad": 0.144,
        "offset": 0,
    }

    # Create a time basis: 1050 data points from 0 to 21 ms
    time = np.arange(0, 21, 0.02)

    # Generate synthetic data from the energy transfer model
    data_2pt5pct = general_energy_transfer(
        time, interaction_components2pt5pct, const_dict1
    )
    data_5pct = general_energy_transfer(time, interaction_components5pct, const_dict2)

    # Add some noise to make it more realistic
    rng = np.random.default_rng()
    noise = 0.01 * rng.normal(size=time.size)
    data_2pt5pct = data_2pt5pct + noise
    data_5pct = data_5pct + noise

    # Plot the synthetic data
    fig4 = Plot()
    fig4.transient(time, data_2pt5pct)
    fig4.transient(time, data_5pct)
    fig4.show()

    # =========================================================================
    # 8. Fit the data using the Optimiser
    # =========================================================================
    # Define independent and dependent parameters:
    # - Shared names ('cr', 'rad') are constrained to be the same across traces
    # - Different names ('amp1'/'amp2', 'offset1'/'offset2') vary independently
    params2pt5pct = ["amp1", "cr", "rad", "offset1"]
    params5pct = ["amp2", "cr", "rad", "offset2"]

    # Create Trace objects: (data, time, label, interaction_components)
    trace2pt5pct = Trace(data_2pt5pct, time, "2.5%", interaction_components2pt5pct)
    trace5pct = Trace(data_5pct, time, "5%", interaction_components5pct)

    # Create the optimiser with the 'rs' (Rust-accelerated) model
    opti = Optimiser([trace2pt5pct, trace5pct], [params2pt5pct, params5pct], model="rs")

    # Provide an initial guess for the unique set of parameters
    guess = {
        "amp1": 1,
        "amp2": 1,
        "cr": 100,
        "rad": 0.500,
        "offset1": 0,
        "offset2": 0,
    }

    # Run the fit
    res = opti.fit(guess, model="rs", method="Nelder-Mead", tol=1e-13)

    # =========================================================================
    # 9. Plot the fitted results
    # =========================================================================
    # Extract the fitted parameters
    rdict = res.x
    print(f"Resulting fitted params: {rdict}")

    fig5 = Plot()
    # Plot the raw data using Trace objects (displayed as markers)
    # Subtract the fitted offset from each trace so the log-scale y-axis
    # doesn't bend downward at long time scales where the constant offset
    # term would otherwise dominate.
    fig5.transient(trace2pt5pct, offset=rdict["offset1"])
    fig5.transient(trace5pct, offset=rdict["offset2"])

    # Generate fitted curves using the optimised parameters
    # Values are accessed by position (insertion order):
    # [0] amplitude, [1] cross_relaxation_rate, [2] radiative_decay_rate, [3] offset
    fit1 = general_energy_transfer(
        time,
        interaction_components2pt5pct,
        {
            "amp": rdict["amp1"],
            "cr": rdict["cr"],
            "rad": rdict["rad"],
            "offset": rdict["offset1"],
        },
    )
    fit2 = general_energy_transfer(
        time,
        interaction_components5pct,
        {
            "amp": rdict["amp2"],
            "cr": rdict["cr"],
            "rad": rdict["rad"],
            "offset": rdict["offset2"],
        },
    )

    # Plot the fitted curves (fit=True displays as lines instead of markers)
    # Subtract the same offsets from the fitted curves to stay consistent
    fig5.transient(time, fit1, fit=True, name="fit 2.5%", offset=rdict["offset1"])
    fig5.transient(time, fit2, fit=True, name="fit 5%", offset=rdict["offset2"])
    fig5.show()
