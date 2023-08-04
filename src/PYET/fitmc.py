import numpy as np
import pandas as pd
import scipy.stats as sc
from numpy.random import normal
import matplotlib.pyplot as plt
from itertools import islice
x = np.arange(0,500,1)
def double_exp_test1(dict):
    global x
    return  list(dict.values())[0]*(np.exp(-list(dict.values())[1]*x)- np.exp(-list(dict.values())[2]*x))
def chi(dict):
    global y 
    global tot_params
    ch = 0
    params = []
    i = 0
  
    for item in chunks(dict, tot_params):

        t = sum(double_exp_test1(item) - y[i])
        i += 1
    ch += t
    return ch
        
  
def chunks(data, SIZE=1000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

    

tot_params = 3


const_dict1  = {'a': 1 , 'b': 0.02, 'c' : 0.83}
const_dict2  = {'a': 2 , 'b': 0.04, 'c' : 1.6}
y1 = double_exp_test1(const_dict1)
y2 = double_exp_test1(const_dict2)
rng = np.random.default_rng()
y_noise = 0.02 * rng.normal(size=x.size)
ydata = y1 + y_noise
ydata2 = y2 + y_noise
plt.plot(x,ydata)
plt.plot(x,ydata2)
plt.show()                
guess = {'a' : 1, 'b': 0.02, 'c': 0.83,'a2' : 2, 'b2': 0.04, 'c2': 1.6}

y = [ydata,ydata2]
'''

Actual code
'''
import scipy.optimize


def dict_least_squares(fn, dict0, *args, **kwargs):
    keys = list(dict0.keys());
    print(keys)
    result = scipy.optimize.least_squares(
        lambda x: fn({k:v for k,v in zip(keys, x)}), # wrap the argument in a dict
        [dict0[k] for k in keys], # unwrap the initial dictionary
        *args, # pass position arguments
        **kwargs # pass named arguments
    )
    # wrap the solution in a dictionary
    try:
        result.x = {k:v for k,v in zip(keys, result.x)}
    except:
        pass
    return result


initial_dict = {"a" : 1, "b" : 0.02, "c" : 0.83}
chi(guess)
res = dict_least_squares(chi, guess)
print(res.x)
class Trace:
    def __init__(self, trace, fname, parser = False):
        self.trace = trace
        self.name = fname
        if parser == True:
            self.trace = self.parse(self.trace)

        def parse(self, trace):
            print('not yet implemented')  
    
    
class Optimiser:
     
    def __init__(self, Traces, model, total_params):
      self.Traces = Traces
      self.model = model
      self.params = {}
    
    def constructor(self, independent_params, dependent_params):
          self.model_params = []
          i = 0
          for trace in self.Traces:
                for param in independent_params:
                  param = param + f'_{i}'
    
                  self.model_params.append(param)  
                for param in dependent_params:    
                   self.model_params.append(param) 
                
                i += 1

            





                

             


#yest = Trace(ydata2, 'stack1')
#nest = Trace(ydata2, 'stack2')
#opti = Optimiser([yest,nest],double_exp_test1, 3).constructor(['amplitude'], ['decay1', 'decay2'])
