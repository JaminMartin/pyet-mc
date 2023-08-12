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

# Model functions for testing and general use
def test_double_exp(time,dictionary):
 
    return  list(dictionary.values())[0]*(np.exp(-list(dictionary.values())[1]*time)- np.exp(-list(dictionary.values())[2]*time))


def general_energy_transfer(time, radial_data, dictionary):
    n = len(radial_data)
    exponentials = np.exp(-1 * time[:, np.newaxis] * (list(dictionary.values())[1] * radial_data + list(dictionary.values())[2]))
    result = list(dictionary.values())[0] / n * np.sum(exponentials, axis=1) + list(dictionary.values())[3]
    return result

        

'''

Actual code
'''
#data structure for handling experimental data & radial info
class Trace:
    def __init__(self, ydata, xdata, fname, radial_data, parser = False):
        self.trace = ydata
        self.name = fname
        self.time = xdata
        self.radial_data = radial_data
        if parser == True:
            self.trace = self.parse(self.trace)

        def parse(self, trace):
            print('not yet implemented')  
    
#class for handling the fitting, plotting & logging results 
class Optimiser:
     
    def __init__(self, Traces, variables, model = 'default'):
      self.Traces = Traces #list of numpy array containing experimental data
      self.variables = variables #list of variables for each trace
      if model == 'default':
          self.model = general_energy_transfer
      else:
          self.model = model    



    def fit(self, guess,  *args, **kwargs):
        keys = list(guess.keys())
        print(keys)
        print(f'Guess with initial params:{guess}')
        fn = self.chi
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
        return self.result

            
    def chi(self,dictionary):
        

        total_traces = len(self.Traces)

        ch = 0
        
        
        for j in range(total_traces):
            keys = self.variables[j]
            
            #print(keys)
            temp_dict = {key: dictionary[key] for key in keys}
            #print(temp_dict)

            #temp_dict2 ={k:v for k,v in zip(keys, result.x)}
            ch += np.sum(((self.model(self.Traces[j].time,self.Traces[j].radial_data, temp_dict) - self.Traces[j].trace)**2))
            
        #print(ch)
        return ch




                

             
#TODO add plot rendering & output logging to fitting

if __name__ == "__main__":
# testing 
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache'))
    with open(f'{cache_dir}/singlecross_10_5_QQ_50000.json') as json_file:
        dict = json.load(json_file)
        interact1 = np.asarray(dict['r_components'])
    with open(f'{cache_dir}/singlecross_10_2pt5_QQ_50000.json') as json_file:
        dict = json.load(json_file)
        interact2 = np.asarray(dict['r_components'])    
    const_dict1  = {'a': 1 , 'b': 3e9, 'c' : 144, 'd':0}
    const_dict2  = {'a': 1 , 'b': 3e9, 'c' : 144, 'd': 0}
    start = timer()
    #res = dict_opt(chi, guess, tol = 1e-12)
    x = np.arange(0,0.01,0.00001)
    print(len(x))
    y1 = general_energy_transfer(x, interact1, const_dict1)
    y2 = general_energy_transfer(x, interact2, const_dict2)
    rng = np.random.default_rng()
    y_noise = 0.01 * rng.normal(size=x.size)
    ydata1 = y1 + y_noise
    ydata2 = y2 + y_noise
    dt = timer() - start
    print ("Datageneration ran in %f s" % dt)   

    data1 = Trace(ydata1, x,  '2%', interact1)
    data2 = Trace(ydata2, x, '5%', interact2)
    y1dep = ['amp1', 'decay1', 'decay2', 'offset1']
    y2dep = ['amp2', 'decay1', 'decay2', 'offset2']
    opti = Optimiser([data1,data2],[y1dep,y2dep], model = 'default')
    guess = {'amp1': 1, 'amp2': 1, 'decay1': 2e9,'decay2' : 500, 'offset1': 0 , 'offset2': 0}
    start = timer()
    #res = opti.fit(guess, method = 'Nelder-Mead', tol = 1e-13)
    dt = timer() - start
    print ("Unoptimised python implementation ran in %f s" % dt)
    print(f'resulting fitted params:{res.x}')
    resultdict = res.x
    plt.plot(x,ydata2, label='2.5%')
    plt.plot(x,ydata1,  label='5%')
    plt.plot(x, general_energy_transfer(x, interact1, {'a': resultdict['amp1'], 'b': resultdict['decay1'], 'c': resultdict['decay2'],'d': resultdict['offset1']}))
    plt.plot(x, general_energy_transfer(x, interact2, {'a': resultdict['amp2'], 'b': resultdict['decay1'], 'c': resultdict['decay2'], 'd': resultdict['offset2']}))
    plt.yscale('log')
    plt.xlabel('Time (s)')
    plt.ylabel('Intensity (arb. units.)')
    plt.legend() 
    plt.show()