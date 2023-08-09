import os
import sys
import json
import numpy as np

cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache'))

if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

def cache_writer(r, **params):
    file_name = f'{params["process"]}_{params["radius"]}_{params["concentration"]}_{params["interaction_type"]}_{params["iter"]}'
    temp = {}
    temp['r_components'] = r.tolist()
    dictionary = params | temp
    with open(f'{cache_dir}/{file_name}.json', 'w') as fp:
        json.dump(dictionary, fp)
    
     

def cache_reader(**params):
    directory = cache_dir
    vmat = ([params["process"],str(params["radius"]),str(params["concentration"]),str(params["interaction_type"]),str(params["iter"])])
    data = None
    try:
        for filename in os.listdir(directory):
            tempTuple = os.path.splitext(filename)
            filename = tempTuple[0]
            temp = filename.split("_")
            if vmat == temp:
                with open(f'{directory}/{filename}.json') as json_file:
                    dict = json.load(json_file)
                    print('file found in cache, not running simulation')
                    data = np.asarray(dict['r_components'])
                    break
            else:
                pass  
         
    except:
         print('File not found')
         pass
    return data    



#array = np.array([1,2,3,4,5])
#d1 = cache_writer(array, process = 'sim_single_cross' , radius=10, concentration = 5, interaction_type='DD', iter=5)
