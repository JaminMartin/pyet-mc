import os
import sys
import json
import numpy as np
if not os.path.exists('cache'):
    os.mkdir('cache')

def cache_writer(r, **params):
    file_name = f'{params["process"]}_{params["radius"]}_{params["concentration"]}_{params["interaction_type"]}_{params["iter"]}'
    temp = {}
    temp['r_components'] = r.tolist()
    dictionary = params | temp
    with open(f'cache/{file_name}.json', 'w') as fp:
        json.dump(dictionary, fp)
    
     

def cache_reader(**params):
    return 

array = np.array([1,2,3,4,5])
d1 = cache_writer(array, process = 'sim_single_cross' , radius=10, concentration = 5, interaction_type='DD', iter=5)

