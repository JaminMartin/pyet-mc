import numpy as np
import pandas as pd
import scipy.stats as sc
from numpy.random import normal
import matplotlib.pyplot as plt
from itertools import islice
x = np.arange(0,200,1)
def double_exp_test1(dict):
    global x
    return  list(dict.values())[0]*(np.exp(-list(dict.values())[1]*x)- np.exp(-list(dict.values())[2]*x))


def chi(dict):
    
    global y 
    global deps
    total_traces = len(y)
    ch = 0
    

    for j in range(total_traces):
        keys = deps[j]
        #print(keys)
        temp_dict = {'a': dict[keys[0]], 'b':dict[keys[1]] , 'c' :dict[keys[2]]}
        #print(temp_dict)


        ch += np.sum(((double_exp_test1(temp_dict) - y[j])**2))
   
    #print(ch)
    return ch
        
  
def chunks(data, SIZE=1000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

    


const_dict1  = {'a': 1 , 'b': 0.02, 'c' : 0.83}
const_dict2  = {'a': 5 , 'b': 0.02, 'c' : 0.83}
y1 = double_exp_test1(const_dict1)
y2 = double_exp_test1(const_dict2)
rng = np.random.default_rng()
y_noise = 0.02 * rng.normal(size=x.size)
ydata = y1 + y_noise
ydata2 = y2 + y_noise
            
guess = {'amp1': 20, 'amp2': 4, 'decay1': 3,'decay2' : 2}
y1dep = ['amp1', 'decay1', 'decay2']
y2dep = ['amp2', 'decay1', 'decay2']
deps = [y1dep, y2dep]
y = [ydata, ydata2]
'''

Actual code
'''
import scipy.optimize


def dict_opt(fn, dict0, *args, **kwargs):
    keys = list(dict0.keys());
    print(keys)
    print(f'Guess with initial params:{dict0}')
    result = scipy.optimize.minimize(
        
        lambda x: fn({k:v for k,v in zip(keys, x)}), # wrap the argument in a dict
        [dict0[k] for k in keys], # unwrap the initial dictionary
        method='Nelder-Mead',
        *args, # pass position arguments
        **kwargs # pass named arguments
    )
    # wrap the solution in a dictionary
    try:
        result.x = {k:v for k,v in zip(keys, result.x)}
    except:
        pass
    return result


chi(guess)
res = dict_opt(chi, guess, tol = 1e-12)
print(f'resulting fitted params:{res.x}')
resultdict = res.x
plt.plot(x,ydata)
plt.plot(x,ydata2)
plt.plot(x, double_exp_test1({'a': resultdict['amp1'], 'b': resultdict['decay1'], 'c': resultdict['decay2']}))
plt.plot(x, double_exp_test1({'a': resultdict['amp2'], 'b': resultdict['decay1'], 'c': resultdict['decay2']}))
plt.show()
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
          return self.model_params      

            





                

             


yest = Trace(ydata2, 'stack1')
nest = Trace(ydata2, 'stack2')
opti = Optimiser([yest,nest],double_exp_test1, 3).constructor(['amplitude'], ['decay1', 'decay2'])
#print(opti)