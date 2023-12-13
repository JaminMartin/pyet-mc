import os
import sys
import json
import numpy as np
import glob
import random as rd
import scipy.stats as stats
cache_dir_path = os.path.join(os.path.dirname(__file__), 'cache')

if not os.path.exists(cache_dir_path):
    os.makedirs(cache_dir_path)

cache_dir = os.path.abspath(cache_dir_path)

class Trace:
    """
    The Trace class represents a trace of experimental data points, it allows provides some basic functionalaity to aid in plotting (through naming) and data parsing for manipulating in various ways prior to fitting.

    Attributes:
    trace (np.ndarray): The y-coordinates of the data points.
    name (str): The name of the trace.
    time (np.ndarray): The x-coordinates (time points) of the data points.
    radial_data (np.ndarray): The radial data associated with the trace, this would be pre-calculated based on the concentration of the sample.
    """
    def __init__(self, ydata: np.ndarray, xdata: np.ndarray, fname: str, radial_data: np.ndarray, weighting: int = 1, parser = False):
        """
        The constructor for the Trace class.

        Parameters:
        ydata (np.ndarray): The y-coordinates of the data points.
        xdata (np.ndarray): The x-coordinates (time points) of the data points.
        fname (str): The name of the trace.
        radial_data (np.ndarray): The radial data associated with the trace, this would be pre-calculated based on the concentration of the sample.
        parser (bool, optional): A flag indicating whether to parse the trace data. Defaults to False.
        """
        self.weight = weighting
        self.trace = ydata
        self.name = fname
        self.time = xdata
        self.radial_data = radial_data
        if parser == True:
            self.trace = self.parse(self.trace)

        def parse(self, trace):
            print('not yet implemented')  

def cache_writer(r, **params):

    file_name = f'{params["process"]}_{params["radius"]}_{params["concentration"]}_{params["interaction_type"]}_{params["iterations"]}_intrinsic_{params["intrinsic"]}'
    file_name = file_name.replace('.', 'pt')
    temp = {}
    temp['r_components'] = r.tolist()
    dictionary = params | temp
    with open(f'{cache_dir}/{file_name}.json', 'w') as fp:
        json.dump(dictionary, fp)
    
     

def cache_reader(**params):
    directory = cache_dir

    vmat = ([params["process"],str(params["radius"]),str(params["concentration"]),str(params["interaction_type"]),str(params["iterations"]),"intrinsic", str(params["intrinsic"])])
    for i in range(len(vmat)):
        vmat[i] = vmat[i].replace('.', 'pt')
    data = None
    try:
        for filename in os.listdir(directory):
            tempTuple = os.path.splitext(filename)
            filename = tempTuple[0]
            temp = filename.split("_")
    
        
            if vmat == temp:
                with open(f'{directory}/{filename}.json') as json_file:
                    dict = json.load(json_file)
                    print('file found in cache, returning interaction components')
                    data = np.asarray(dict['r_components'])
                    break
            else:
                pass  
        if data is None:
            raise 
    except:
         print('File not found, check your inputs or consider running a simulation with these parameters')
         pass
    return data    


def cache_clear(**params):
    directory = cache_dir
    if not params:
        # delete all cache files
        print('Are you sure you want to delete all the cache files? [Y/N]?')
        res = input()
        match res: 
            case 'Y' | 'y':
                for file in os.listdir(directory):
                    if file.endswith('.json'):
                        os.remove(os.path.join(directory, file))
            case 'N' | 'n':
                # do not delete cache files
                pass
            case _:
                # invalid input
                print('Invalid input. Please enter "Y" or "N".')            
    else:
        vmat = ([params["process"],str(params["radius"]),str(params["concentration"]),str(params["interaction_type"]),str(params["iterations"]),str(params["intrinsic"])])
        for i in range(len(vmat)):
            vmat[i] = vmat[i].replace('.', 'pt')
        vmat_str = '_'.join(vmat)    
        file_name = f'{vmat_str}.json'
        
        print(f'Trying to delete file: {file_name}')
        try:
            for file in os.listdir(directory):
                if file == file_name:
                    os.remove(os.path.join(directory, file))
        except:
            print('File not found, check your inputs or consider running a simulation with these parameters')
            pass

def cache_list():
    directory = cache_dir
    files = glob.glob(f"{directory}/*.json") 
    print('#======# Cached Files #======#')
    total_size = 0
    for file in files:
        file_size = os.path.getsize(file)
        total_size += file_size
        print(os.path.basename(file), f'({file_size} bytes)')
    total_size_mb = total_size / 1000000
    print(f'Total cache size: {total_size_mb:.2f} MB')
    print('Run "cache_clear()" to clear the cache')
    print('#============================#')



def Gamma2sigma(Gamma: float) -> float:
    '''Function to convert FWHM (Gamma) to standard deviation (sigma) for stats.norm'''
    return Gamma * np.sqrt(2) / ( np.sqrt(2 * np.log(2)) * 2 )

def random_spectra(wavelength: np.ndarray, wavenumbers: bool = False) -> np.ndarray: 
    
    #generates a random spectra (optimised for nm) for the scaned wavelength range. Generates 5 peaks, though they may not be resolved

    sigma1 = Gamma2sigma(rd.uniform(0.1, 5)) 
    sigma2 = Gamma2sigma(rd.uniform(0.1, 5)) 
    sigma3 = Gamma2sigma(rd.uniform(0.1, 5)) 
    sigma4 = Gamma2sigma(rd.uniform(0.1, 5)) 
    sigma5 = Gamma2sigma(rd.uniform(0.1, 5)) 


    LINE1 = stats.norm.pdf(wavelength,rd.uniform(np.min(wavelength)+10,np.max(wavelength)-10), sigma1) * 1000
    LINE2 = stats.norm.pdf(wavelength,rd.uniform(np.min(wavelength)+10,np.max(wavelength)-10), sigma2) * 1000 
    LINE3 = stats.norm.pdf(wavelength,rd.uniform(np.min(wavelength)+10,np.max(wavelength)-10), sigma3) * 1000
    LINE4 = stats.norm.pdf(wavelength,rd.uniform(np.min(wavelength)+10,np.max(wavelength)-10), sigma4) * 1000 
    LINE5 = stats.norm.pdf(wavelength,rd.uniform(np.min(wavelength)+10,np.max(wavelength)-10), sigma5) * 1000
    LINE_TOT = LINE1 + LINE2 + LINE3 + LINE4 + LINE5

    if wavenumbers:
       wavelength = (1 / wavelength) * 10_000_000
    return wavelength, LINE_TOT

if __name__ == "__main__":
    
    cache_list()
    cache_reader(process = 'singlecross', radius = 20, concentration = 5, iterations = 50000, interaction_type = "DQ", intrinsic = False) 