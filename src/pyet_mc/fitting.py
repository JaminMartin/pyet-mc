import numpy as np
import pandas as pd
import scipy.stats as sc
from numpy.random import normal
import matplotlib.pyplot as plt
from itertools import islice
import json
from timeit import default_timer as timer
import scipy.optimize
import os
from typing import Union, Optional, List, Dict, Callable
from .pyet_utils import Trace, fit_logger
from .plotting import Plot
import warnings
import datetime

try:
    from pyet_mc import _pyet_mc as pyrs
    general_energy_transfer_para = pyrs.general_energy_transfer_para
    use_rust_library = True

except ImportError:
    use_rust_library = False
    general_energy_transfer_para = None
    warnings.warn("Failed to import 'general_energy_transfer_para' from 'pyet_rs'. The performance-optimized version of the function will not be used.")

# Model functions for testing and general use
def test_double_exp(time: np.ndarray ,dictionary: Dict) -> np.ndarray:
    """
    This function calculates and returns the result of a double exponential function.

    Parameters:
    time (np.ndarray): The time value used in the exponential calculation.
    dictionary (dict): A dictionary containing the coefficients used in the calculation. The dictionary should have at least three values.
    The dictionary contains the parameters that define the exponential A*(e^-p*x - e^-q*x)
    Amplitude: A
    First decay rate: p
    Second decay rate: q
    Returns:
    np.ndarray: The result of the calculation as a numpy array.
    """
    return  list(dictionary.values())[0]*(np.exp(-list(dictionary.values())[1]*time)- np.exp(-list(dictionary.values())[2]*x))

# default energy transfer function
def general_energy_transfer(time: np.ndarray, radial_data:  np.ndarray, dictionary: Dict) -> np.ndarray:
    """
    This function calculates and returns the result of a double exponential function.
    Parameters:
    time (np.ndarray): The time value used in the exponential calculation.
    dictionary (dict): A dictionary containing the coefficients used in the calculation. The dictionary should have at least four values.
    The dictionary contains the parameters that define the exponential A*(e^-Cr*r_i*t - e^-Rad*t)+c
    Amplitude: A
    Cross relaxation rate: Cr
    Radiative relaxation rate: Rad
    Offset: c
    Returns:
    np.ndarray: The result of the calculation as a numpy array.
    """
    n = len(radial_data)
    exponentials = np.exp(-1 * time[:, np.newaxis] * (list(dictionary.values())[1] * radial_data + list(dictionary.values())[2]))
    result = list(dictionary.values())[0] / n * np.sum(exponentials, axis=1) + list(dictionary.values())[3]
    return result

        

'''

Actual code
'''
#class for handling the fitting, plotting & logging results 
class Optimiser:
    """
    The Optimiser class handles the fitting, plotting, and logging of results.

    Attributes:
    Traces (list): A list of Trace objects containing experimental data.
    variables (list): A list of variables for each trace.
    model (function): The model function used to describe the energy transfer process. Defaults to 'general_energy_transfer'.
    """ 
    def __init__(self, traces: List[Trace], variables: List[str], auto_weights: bool = True,  model: Union[str, Callable[...,np.ndarray]] = 'default'):
      self.traces = traces #list of numpy array containing experimental data
      self.variables = variables #list of variables for each trace
      if auto_weights:
          self.adjust_weights()
      if model == 'default':
          self.model = general_energy_transfer
      elif model == 'rs':
          self.model = general_energy_transfer_para    
      else:
          self.model = model    


    def adjust_weights(self):
        """
        Adjusts the weights of the traces based on their lengths.
        """
        # Get the length of the longest trace
        max_length = max(len(trace.time) for trace in self.traces)
      
        # Adjust the weights of the traces to correct for differences in lenght. 
        for trace in self.traces:
           
            length_based_weight = max_length / len(trace.time)
            trace.weight *= length_based_weight
            print(f'the weights of the {trace.name} trace have been adjusted to {trace.weight}')

    def fit(self, guess: Dict, bounds: Dict = {}, solver = 'minimize', *args, **kwargs) -> Dict:
        """
        The fit method performs the fitting process using the provided initial guess and optional arguments.
        Note this is a decoupled/decoupled fit if multiple traces are provided. It will aim to fit all traces parameters (that are the same) simultanously
        Parameters:
        guess (dict): A dictionary containing the initial guess for the parameters.
        *args: Optional positional arguments passed to the scipy.optimize.minimize function.
        **kwargs: Optional keyword arguments passed to the scipy.optimize.minimize function.

        Returns:
        result (OptimizeResult): The result of the optimization process.
        """
        bound_values = list(bounds.values())
        keys = list(guess.keys())
        print(keys)
        print(f'Guess with initial params:{guess}')
        print('Started fitting...')
        fn = self.wrss

        temp_res = {'Initialised time': str(datetime.datetime.now())}
        temp_res['bounds'] = bounds
        temp_res['guess'] = guess
        temp_res['solver'] = solver
        temp_res['args'] = args
        temp_res['kwargs'] = kwargs
        temp_res['Trace_info'] = {}
        for trace in self.traces:
            temp_res['Trace_info'][trace.name] = {'weighting': trace.weight, 'processing': trace.parser}
        match solver:
            case 'minimize':
                self.result = scipy.optimize.minimize(
                    
                    lambda x: fn({k:v for k,v in zip(keys, x)}), # wrap the argument in a dict
                    [guess[k] for k in keys], # unwrap the initial dictionary
                    
                    
                    *args, # pass position arguments
                    **kwargs # pass named arguments
                )
                # wrap the solution in a dictionary
                try:
                    self.result.x = {k:v for k,v in zip(keys, self.result.x)}
                except:
                    pass
                
            case 'basinhopping':
                self.result = scipy.optimize.basinhopping(
                    
                    lambda x: fn({k:v for k,v in zip(keys, x)}), # wrap the argument in a dict
                    [guess[k] for k in keys], # unwrap the initial dictionary
                    
                    
                    *args, # pass position arguments
                    **kwargs # pass named arguments
                )
                # wrap the solution in a dictionary
                try:
                    self.result.x = {k:v for k,v in zip(keys, self.result.x)}
                except:
                    pass
             
            
            case 'differential_evolution':
                self.result = scipy.optimize.differential_evolution(
                    
                    lambda x: fn({k:v for k,v in zip(keys, x)}), # wrap the argument in a dict
                    bound_values,
                    x0 = [guess[k] for k in keys], # unwrap the initial dictionary
                    
                    *args, # pass position arguments
                    **kwargs # pass named arguments
                )
                # wrap the solution in a dictionary
                try:
                    self.result.x = {k:v for k,v in zip(keys, self.result.x)}
                except:
                    pass
           
            
            case 'dual_annealing':

                self.result = scipy.optimize.dual_annealing(
                    
                    lambda x: fn({k:v for k,v in zip(keys, x)}), # wrap the argument in a dict
                    bound_values,
                    x0 = [guess[k] for k in keys], # unwrap the initial dictionary
                    
                    *args, # pass position arguments
                    **kwargs # pass named arguments
                )
                # wrap the solution in a dictionary
                try:
                    self.result.x = {k:v for k,v in zip(keys, self.result.x)}
                except:
                    pass
             
            case _:
                print('not a supported case')

        temp_res['results'] = self.result 
        #print(f'The resulting summary dict: {temp_res}')   
        self.uncertainties()     
        temp_res['uncertainties'] =  self.uncertainty
        fit_logger(temp_res)
        return self.result  


    def uncertainties(self) -> dict:
        max_iterations = 1000
        original_wrss = self.result.fun.copy()
        self.uncertainty = {}
        print("calculating uncertainites...")
        for k , v in self.result.x.items():
            res_for_uncertainty = self.result.x.copy()
            binary_init = 5
            new_val = v + (v * binary_init)
            res_for_uncertainty[k] = new_val
            iterations = 0
            new_wrss = self.wrss(res_for_uncertainty)
            relative_change  = abs(new_wrss - original_wrss) / original_wrss
           
            while not (0.04 < relative_change < 0.05) and iterations < max_iterations:
              
                if relative_change > 0.05:
                   
                   binary_init = binary_init * 0.5
                elif relative_change < 0.04:
                   
                    binary_init = binary_init * 1.5
        
                new_val = v + (v * binary_init)
                res_for_uncertainty[k] = new_val 
                new_wrss = self.wrss(res_for_uncertainty)
                relative_change  = abs(new_wrss - original_wrss) / original_wrss
                iterations += 1

            self.uncertainty[k] = v * binary_init
        return    






                        
    def wrss(self,dictionary):
        """
        The wrss method calculates the weighted reduced sum of squares value for the current set of parameters.

        Parameters:
        dictionary (dict): A dictionary containing the current set of parameters.

        Returns:
        rs (float): The calculated weighted reduced sum of squares value.
        """

        total_traces = len(self.traces)

        rs = 0
        
        if self.model != general_energy_transfer_para:
            for j in range(total_traces):
                keys = self.variables[j]
                
                #print(keys)
                temp_dict = {key: dictionary[key] for key in keys}
                #print(temp_dict)

                #temp_dict2 ={k:v for k,v in zip(keys, result.x)}
                rs += self.traces[j].weight * np.sum(((self.model(self.traces[j].time, self.traces[j].radial_data, temp_dict) - self.traces[j].trace)**2))
                
            #print(ch)
        else:
            for j in range(total_traces):
                keys = self.variables[j]
                
                #print(keys)
                temp_dict = {key: dictionary[key] for key in keys}
                #print(temp_dict)
                time_rs = self.traces[j].time.tolist()
                radial_rs = self.traces[j].radial_data.tolist()
                #temp_dict2 ={k:v for k,v in zip(keys, result.x)}
                values = list(map(float, temp_dict.values()))

                rs += self.traces[j].weight * np.sum((self.model(time_rs, radial_rs, values[0], values[1], values[2], values[3]) - self.traces[j].trace)**2)

           
        return rs



                


if __name__ == "__main__":
# testing 
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cache'))
    with open(f'{cache_dir}/singlecross_10_2pt5_DQ_50000_intrinsic_False_20240519115427.json') as json_file:
        dict = json.load(json_file)
        interact1 = np.asarray(dict['r_components'])
    with open(f'{cache_dir}/singlecross_10_5_DQ_50000_intrinsic_False_20240519115504.json') as json_file:
        dict = json.load(json_file)
        interact2 = np.asarray(dict['r_components'])    
    const_dict1  = {'a': 1 , 'b': 490, 'c' : 0.144, 'd':0}
    const_dict2  = {'a': 1 , 'b': 490, 'c' : 0.144, 'd': 0}
    start = timer()
    #res = dict_opt(chi, guess, tol = 1e-12)
    x = np.arange(0,21,0.02)
    x2 = np.arange(0,21,0.02)
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
    print ("Datageneration ran in %f s" % dt)   


    data1 = Trace(ydata1, x,  '2.5%', interact1)
    data2 = Trace(ydata2, x2, '5%', interact2)
    y1dep = ['amp1', 'cr', 'rad', 'offset1']
    y2dep = ['amp2', 'cr', 'rad', 'offset2']
    bounds = {'amp1': (0,100),'amp2':(0,100),'cr':(0,1000000),'rad':(0,1000000),'offset1':(-10000,10000),'offset2':(-10000,10000)}
    opti = Optimiser([data1,data2],[y1dep,y2dep], model = 'rs', auto_weights=False)
    guess = {'amp1': 1, 'amp2': 1, 'cr': 400,'rad' : 0.500, 'offset1': 0 , 'offset2': 0}

    
    start = timer()
    res = opti.fit(guess, solver  = 'minimize', method = 'Nelder-Mead', tol = 1e-16)
    dt = timer() - start
    print ("Unoptimised python implementation ran in %f s" % dt)
    print(f'resulting fitted params:{res.x}')
    resultdict = res.x
    fit1 = general_energy_transfer(x, interact1, {'a': resultdict['amp1'], 'b': resultdict['cr'], 'c': resultdict['rad'],'d': resultdict['offset1']})
    fit2 = general_energy_transfer(x, interact2, {'a': resultdict['amp2'], 'b': resultdict['cr'], 'c': resultdict['rad'], 'd': resultdict['offset2']})

    data1.time = data1.time
    data2.time = data2.time
    fig = Plot()
    fig.transient(data1)
    fig.transient(data2)
    fig.transient(x,fit1, fit=True, name = 'fit 2.5%')
    fig.transient(x,fit2, fit = True, name = 'fit 5%')
    fig.show()
