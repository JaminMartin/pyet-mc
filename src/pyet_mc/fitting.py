import datetime
import json
import os
import warnings
from timeit import default_timer as timer
from typing import Callable, Dict, List, Optional, Union

import numpy as np
import scipy.optimize

from .plotting import Plot
from .pyet_utils import Trace, fit_logger

try:
    from pyet_mc import _pyet_mc as pyrs

    general_energy_transfer_para = pyrs.general_energy_transfer_para
    general_energy_transfer_rs = pyrs.general_energy_transfer
    use_rust_library = True

except ImportError:
    use_rust_library = False
    general_energy_transfer_para = None
    general_energy_transfer_rs = None
    warnings.warn(
        "Failed to import Rust bindings from 'pyet_mc._pyet_mc'. The performance-optimized version of the function will not be used."
    )


# --------------------------------------------------------------------------- #
# Rust wrapper functions — unified (time, radial_data, dict) calling convention
# --------------------------------------------------------------------------- #


def _rust_energy_transfer(time, radial_data, dictionary):
    """Wrapper around the sequential Rust general_energy_transfer that accepts the same
    (time, radial_data, dict) calling convention as the Python model.

    Values are extracted by position (insertion order), matching the contract
    of general_energy_transfer: [0] amp, [1] cr, [2] rad, [3] offset.
    """
    time_list = time.tolist() if hasattr(time, "tolist") else list(time)
    radial_list = (
        radial_data.tolist() if hasattr(radial_data, "tolist") else list(radial_data)
    )
    vals = list(map(float, dictionary.values()))
    return np.array(
        general_energy_transfer_rs(
            time_list,
            radial_list,
            vals[0],
            vals[1],
            vals[2],
            vals[3],
        )
    )


def _rust_energy_transfer_para(time, radial_data, dictionary):
    """Wrapper around the parallel Rust general_energy_transfer_para that accepts the same
    (time, radial_data, dict) calling convention as the Python model.

    Values are extracted by position (insertion order), matching the contract
    of general_energy_transfer: [0] amp, [1] cr, [2] rad, [3] offset.
    """
    time_list = time.tolist() if hasattr(time, "tolist") else list(time)
    radial_list = (
        radial_data.tolist() if hasattr(radial_data, "tolist") else list(radial_data)
    )
    vals = list(map(float, dictionary.values()))
    return np.array(
        general_energy_transfer_para(
            time_list,
            radial_list,
            vals[0],
            vals[1],
            vals[2],
            vals[3],
        )
    )


# --------------------------------------------------------------------------- #
# Model functions for testing and general use
# --------------------------------------------------------------------------- #


def double_exp(time: np.ndarray, dictionary: Dict) -> np.ndarray:
    """
    This function calculates and returns the result of a double exponential function.

    Parameters:
    time (np.ndarray): The time value used in the exponential calculation.
    dictionary (dict): A dictionary containing the coefficients used in the calculation.
        The dictionary should have at least three values.
    The dictionary contains the parameters that define the exponential A*(e^-p*x - e^-q*x)
    Values are accessed by position (insertion order):
    [0] Amplitude
    [1] First decay rate
    [2] Second decay rate

    Returns:
    np.ndarray: The result of the calculation as a numpy array.
    """
    vals = list(dictionary.values())
    return vals[0] * (np.exp(-vals[1] * time) - np.exp(-vals[2] * time))


# default energy transfer function
def general_energy_transfer(
    time: np.ndarray, radial_data: np.ndarray, dictionary: Dict
) -> np.ndarray:
    """
    This function calculates and returns the result of a generalised energy transfer model.

    Parameters:
    time (np.ndarray): The time value used in the exponential calculation.
    radial_data (np.ndarray): Array of radial distance components from Monte Carlo simulation.
    dictionary (dict): A dictionary containing the coefficients used in the calculation.
        The dictionary should have at least four values.
    The dictionary contains the parameters that define the expression:
        A / N * sum_i(exp(-t * (Cr * r_i + Rad))) + offset
    Values are accessed by position (insertion order):
    [0] Amplitude
    [1] Cross relaxation rate
    [2] Radiative relaxation rate
    [3] Offset

    Returns:
    np.ndarray: The result of the calculation as a numpy array.
    """
    vals = list(dictionary.values())
    n = len(radial_data)
    exponentials = np.exp(-1 * time[:, np.newaxis] * (vals[1] * radial_data + vals[2]))
    result = vals[0] / n * np.sum(exponentials, axis=1) + vals[3]
    return result


# class for handling the fitting, plotting & logging results
class Optimiser:
    """
    The Optimiser class handles the fitting, plotting, and logging of results.

    Attributes:
    Traces (list): A list of Trace objects containing experimental data.
    variables (list): A list of variables for each trace.
    model (function): The model function used to describe the energy transfer process.
        Defaults to 'general_energy_transfer'. All models must accept (time, radial_data, dict).
    """

    def __init__(
        self,
        traces: List[Trace],
        variables: List[str],
        auto_weights: bool = True,
        model: Union[str, Callable[..., np.ndarray]] = "default",
    ):
        self.traces = traces  # list of numpy array containing experimental data
        self.variables = variables  # list of variables for each trace
        if auto_weights:
            self.adjust_weights()
        if model == "default":
            self.model = general_energy_transfer
        elif model == "rs":
            self.model = _rust_energy_transfer_para
        elif model == "rs_single":
            self.model = _rust_energy_transfer
        else:
            self.model = model

    def adjust_weights(self):
        """
        Adjusts the weights of the traces based on their lengths.
        """
        # Get the length of the longest trace
        max_length = max(len(trace.time) for trace in self.traces)

        # Adjust the weights of the traces to correct for differences in length.
        for trace in self.traces:
            length_based_weight = max_length / len(trace.time)
            trace.weight *= length_based_weight
            print(
                f"the weights of the {trace.name} trace have been adjusted to {trace.weight}"
            )

    def _run_solver(self, solver, fn, keys, guess_values, bound_values, args, kwargs):
        """Run the specified scipy solver and return the result with .x wrapped as a named dict.

        Parameters:
        solver (str): Name of the solver to use.
        fn (callable): The objective function that accepts a dict of parameters.
        keys (list): Parameter names.
        guess_values (list): Initial guess values (ordered to match keys).
        bound_values (list): Bounds values (ordered to match keys), used by some solvers.
        args (tuple): Extra positional arguments forwarded to the solver.
        kwargs (dict): Extra keyword arguments forwarded to the solver.

        Returns:
        scipy.optimize.OptimizeResult with .x as a dict mapping parameter names to values.
        """
        objective = lambda x: fn({k: v for k, v in zip(keys, x)})

        match solver:
            case "minimize":
                result = scipy.optimize.minimize(
                    objective, guess_values, *args, **kwargs
                )
            case "basinhopping":
                result = scipy.optimize.basinhopping(
                    objective, guess_values, *args, **kwargs
                )
            case "differential_evolution":
                result = scipy.optimize.differential_evolution(
                    objective, bound_values, x0=guess_values, *args, **kwargs
                )
            case "dual_annealing":
                result = scipy.optimize.dual_annealing(
                    objective, bound_values, x0=guess_values, *args, **kwargs
                )
            case _:
                raise ValueError(
                    f"Unsupported solver: {solver!r}. "
                    f"Supported: 'minimize', 'basinhopping', 'differential_evolution', 'dual_annealing'"
                )

        # Wrap result.x as a named dictionary
        try:
            result.x = {k: v for k, v in zip(keys, result.x)}
        except Exception as e:
            raise RuntimeError(
                f"Failed to wrap optimisation result as a named dictionary. "
                f"Raw result.x = {result.x!r}. Error: {e}"
            ) from e

        return result

    def fit(
        self,
        guess: Dict,
        bounds: Optional[Dict] = None,
        solver="minimize",
        *args,
        **kwargs,
    ) -> scipy.optimize.OptimizeResult:
        """
        The fit method performs the fitting process using the provided initial guess and optional arguments.
        Note this is a decoupled/decoupled fit if multiple traces are provided. It will aim to
        fit all traces parameters (that are the same) simultaneously.

        Parameters:
        guess (dict): A dictionary containing the initial guess for the parameters.
        bounds (dict, optional): A dictionary of parameter bounds. Required for
            'differential_evolution' and 'dual_annealing' solvers.
        solver (str): The solver to use. One of 'minimize', 'basinhopping',
            'differential_evolution', 'dual_annealing'. Defaults to 'minimize'.
        *args: Optional positional arguments passed to the scipy solver.
        **kwargs: Optional keyword arguments passed to the scipy solver.

        Returns:
        scipy.optimize.OptimizeResult: The result of the optimization process,
            with .x as a dict mapping parameter names to fitted values.
        """
        if bounds is None:
            bounds = {}
        bound_values = list(bounds.values())
        keys = list(guess.keys())
        print(keys)
        print(f"Guess with initial params:{guess}")
        print("Started fitting...")
        fn = self.wrss

        temp_res = {"Initialised time": str(datetime.datetime.now())}
        temp_res["bounds"] = bounds
        temp_res["guess"] = guess
        temp_res["solver"] = solver
        temp_res["args"] = args
        temp_res["kwargs"] = kwargs
        temp_res["Trace_info"] = {}
        for trace in self.traces:
            temp_res["Trace_info"][trace.name] = {
                "weighting": trace.weight,
                "processing": trace.parser,
            }

        self.result = self._run_solver(
            solver, fn, keys, [guess[k] for k in keys], bound_values, args, kwargs
        )

        temp_res["results"] = self.result
        self.uncertainties()
        temp_res["uncertainties"] = self.uncertainty
        fit_logger(temp_res)
        return self.result

    def uncertainties(self) -> dict:
        max_iterations = 1000
        original_wrss = self.result.fun.copy()
        self.uncertainty = {}
        print("calculating uncertainites...")
        for k, v in self.result.x.items():
            res_for_uncertainty = self.result.x.copy()
            binary_init = 5
            new_val = v + (v * binary_init)
            res_for_uncertainty[k] = new_val
            iterations = 0
            new_wrss = self.wrss(res_for_uncertainty)
            relative_change = abs(new_wrss - original_wrss) / original_wrss

            while not (0.04 < relative_change < 0.05) and iterations < max_iterations:
                if relative_change > 0.05:
                    binary_init = binary_init * 0.5
                elif relative_change < 0.04:
                    binary_init = binary_init * 1.5

                new_val = v + (v * binary_init)
                res_for_uncertainty[k] = new_val
                new_wrss = self.wrss(res_for_uncertainty)
                relative_change = abs(new_wrss - original_wrss) / original_wrss
                iterations += 1

            self.uncertainty[k] = v * binary_init
        return

    def wrss(self, dictionary):
        """
        The wrss method calculates the weighted reduced sum of squares value
        for the current set of parameters.

        All models (Python, Rust, and custom) are called with the unified signature:
            model(time, radial_data, param_dict)

        Parameters:
        dictionary (dict): A dictionary containing the current set of parameters.

        Returns:
        rs (float): The calculated weighted reduced sum of squares value.
        """

        total_traces = len(self.traces)
        rs = 0

        for j in range(total_traces):
            keys = self.variables[j]
            temp_dict = {key: dictionary[key] for key in keys}

            rs += self.traces[j].weight * np.sum(
                (
                    (
                        self.model(
                            self.traces[j].time,
                            self.traces[j].radial_data,
                            temp_dict,
                        )
                        - self.traces[j].trace
                    )
                    ** 2
                )
            )

        return rs


if __name__ == "__main__":
    # testing
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "cache"))
    with open(
        f"{cache_dir}/singlecross_10_2pt5_DQ_50000_intrinsic_False_20240519115427.json"
    ) as json_file:
        dict = json.load(json_file)
        interact1 = np.asarray(dict["r_components"])
    with open(
        f"{cache_dir}/singlecross_10_5_DQ_50000_intrinsic_False_20240519115504.json"
    ) as json_file:
        dict = json.load(json_file)
        interact2 = np.asarray(dict["r_components"])
    const_dict1 = {"amp": 1, "cr": 490, "rad": 0.144, "offset": 0}
    const_dict2 = {"amp": 1, "cr": 490, "rad": 0.144, "offset": 0}
    start = timer()
    x = np.arange(0, 21, 0.02)
    x2 = np.arange(0, 21, 0.02)
    print(len(x))
    print(len(x2))
    y1 = general_energy_transfer(x, interact1, const_dict1)
    y2 = general_energy_transfer(x2, interact2, const_dict2)
    rng = np.random.default_rng()
    y_noise = 0.01 * rng.normal(size=x.size)
    y2_noise = 0.01 * rng.normal(size=x2.size)
    ydata1 = y1 + y_noise
    ydata2 = y2 + y2_noise
    dt = timer() - start
    print("Datageneration ran in %f s" % dt)

    data1 = Trace(ydata1, x, "2.5%", interact1)
    data2 = Trace(ydata2, x2, "5%", interact2)
    y1dep = ["amp1", "cr", "rad", "offset1"]
    y2dep = ["amp2", "cr", "rad", "offset2"]
    bounds = {
        "amp1": (0, 100),
        "amp2": (0, 100),
        "cr": (0, 1000000),
        "rad": (0, 1000000),
        "offset1": (-10000, 10000),
        "offset2": (-10000, 10000),
    }
    opti = Optimiser([data1, data2], [y1dep, y2dep], model="rs", auto_weights=False)
    guess = {
        "amp1": 1,
        "amp2": 1,
        "cr": 400,
        "rad": 0.500,
        "offset1": 0,
        "offset2": 0,
    }

    start = timer()
    res = opti.fit(guess, solver="minimize", method="Nelder-Mead", tol=1e-16)
    dt = timer() - start
    print("Unoptimised python implementation ran in %f s" % dt)
    print(f"resulting fitted params:{res.x}")
    resultdict = res.x
    fit1 = general_energy_transfer(
        x,
        interact1,
        {
            "amp": resultdict["amp1"],
            "cr": resultdict["cr"],
            "rad": resultdict["rad"],
            "offset": resultdict["offset1"],
        },
    )
    fit2 = general_energy_transfer(
        x,
        interact2,
        {
            "amp": resultdict["amp2"],
            "cr": resultdict["cr"],
            "rad": resultdict["rad"],
            "offset": resultdict["offset2"],
        },
    )

    data1.time = data1.time
    data2.time = data2.time
    fig = Plot()
    fig.transient(data1)
    fig.transient(data2)
    fig.transient(x, fit1, fit=True, name="fit 2.5%")
    fig.transient(x, fit2, fit=True, name="fit 5%")
    fig.show()
