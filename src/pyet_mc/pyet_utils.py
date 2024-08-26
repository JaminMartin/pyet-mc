import os
import sys
import json
import datetime
import numpy as np
import numpy.typing as npt
import glob
import random as rd
import scipy.stats as stats
from datetime import datetime

from typing import Optional
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
        self.parser = "None"
        if parser:
            match parser:
                case 'parse_10':
                    indices = self.parse_10(np.arange(len(self.trace)))
                    self.parser = 'parse_10'
                case 'parse_100':
                    indices = self.parse_100(np.arange(len(self.trace)))
                    self.parser = 'parse_100'
                case 'parse_log':
                    indices = self.parse_log(np.arange(len(self.trace)), 500)
                    self.parser = 'parse_log'
                case _ :
                    print("In correct parsing function these are the currently available parsing functions\n 'parse_10'\n 'parse_100' \n")    
            self.trace = self.trace[indices]
            self.time = self.time[indices]

    def parse_10(self, data):
        return data[0::10]

    def parse_100(self, data):
        return data[0::100]

    def parse_log(self, data, num_samples):
        max_index = len(data) - 1
        return np.unique(np.logspace(0, np.log10(max_index), num_samples, dtype=int))


def cache_writer(r: np.ndarray, sourcefile: str,  **params) -> None:
    """
    Writes data to a file in the cache directory.

    This function constructs a filename from the provided simulation parameters and the current timestamp, and then writes the computed data to a file with that name in the directory.
    The data is written in JSON format, with the 'sourcefile', 'date', and 'r_components' fields containing the source file name, the current date and time, and the interaction data, respectively.

    Args:
        r (np.ndarray): The data to write to the file.
        sourcefile (str): The source file from which the data was computed from.
        **params (Dict[str, Any]): The parameters to construct the filename from.

    Raises:
        FileNotFoundError: If the directory does not exist.
        JSONDecodeError: If the data cannot be serialized to JSON.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f'{params["process"]}_{params["radius"]}_{params["concentration"]}_{params["interaction_type"]}_{params["iterations"]}_intrinsic_{params["intrinsic"]}_{timestamp}'
    file_name = file_name.replace('.', 'pt')
    temp = {}
    temp['sourcefile'] = sourcefile
    temp['date'] = datetime.now().isoformat()
    temp['r_components'] = r.tolist()
    dictionary = params | temp
    with open(f'{cache_dir}/{file_name}.json', 'w') as fp:
        json.dump(dictionary, fp)
    
     

def cache_reader(sourcefile: str, **params) -> np.ndarray:
    """
    Reads cached data from a file in the specified directory.

    This function constructs a filename from the provided parameters, and then tries to find a file with that name in the directory.
    If it finds a file with that name, it reads the data from the file and returns it as a numpy array.
    If it does not find a file with that name, it raises an exception.

    Args:
        sourcefile (str): The source file used to compute the interaction data from.
        **params (Dict[str, Any]): The parameters to construct the filename from, these are the parameters used in the computation of the interaction data.

    Returns:
        np.ndarray: The data read from the file, as a numpy array.

    Raises:
        FileNotFoundError: If the directory or file does not exist.
        JSONDecodeError: If the file does not contain valid JSON.
    """

    directory = cache_dir

    vmat = ([params["process"],str(params["radius"]),str(params["concentration"]),str(params["interaction_type"]),str(params["iterations"]),"intrinsic", str(params["intrinsic"])])
    for i in range(len(vmat)):
        vmat[i] = vmat[i].replace('.', 'pt')
    data = None
    try:
        for filename in os.listdir(directory):
            tempTuple = os.path.splitext(filename)
            filename = tempTuple[0]
            # Remove the timestamp from the filename
            filename_without_timestamp = "_".join(filename.split("_")[:-1])
            temp = filename_without_timestamp.split("_")
    
            with open(f'{directory}/{filename}.json') as json_file:
                dict = json.load(json_file)
                if vmat == temp and dict['sourcefile'] == sourcefile:
                    print('file found in cache, returning interaction components')
                    data = np.asarray(dict['r_components'])
                    break
        if data is None:
            raise 
    except:
         print('File not found, check your inputs or consider running a simulation with these parameters')
         pass
    return data  


def cache_clear(index: Optional[int] = None) -> None:
    """
    Deletes cached files in the specified directory.

    If an index is provided, this function deletes the file at that index.
    The index corresponds to the order of the files sorted by creation date.
    If the index is out of range, it prints an error message and returns.

    If no index is provided, this function asks for confirmation and then deletes all cached files.

    Args:
        index (Optional[int]): The index of the file to delete. If None, all files are deleted.

    Raises:
        JSONDecodeError: If a cached file does not contain valid JSON.
        FileNotFoundError: If the directory or file does not exist.
    """
    directory = cache_dir
    if index is None:

        print('Are you sure you want to delete all the cache files? [Y/N]?')
        res = input()
        match res: 
            case 'Y' | 'y':
                for file in os.listdir(directory):
                    if file.endswith('.json'):
                        os.remove(os.path.join(directory, file))
            case 'N' | 'n':

                pass
            case _:
  
                print('Invalid input. Please enter "Y" or "N".')            
    else:
        directory = cache_dir
        files = glob.glob(f"{directory}/*.json") 
        # Sort files by creation date
        files.sort(key=os.path.getctime)
        if index < 0 or index >= len(files):
            print('Invalid index. Please enter a valid index.')
            return
        file = files[index]
        with open(file, 'r') as f:
            data = json.load(f)
            sourcefile = data.get('sourcefile', 'N/A')
            date = data.get('date', 'N/A')
        print(f'File to delete: {os.path.basename(file)} Source file: {sourcefile}, Date created: {date}')
        print('Are you sure you want to delete this file? [Y/N]')
        res = input()
        match res:
            case 'Y' | 'y':
                os.remove(file)
                print(f'Deleted file: {os.path.basename(file)}')
            case 'N' | 'n':
                print('File not deleted.')


def cache_list() -> None:
    """
    Lists all cached files in the specified directory, sorted by creation date.

    For each file, this function prints its index, name, size in bytes, source file, and creation date.
    It also prints the total size of all cached files in MB and a reminder to run "cache_clear()" to clear the cache.

    This function does not return anything.

    Raises:
        JSONDecodeError: If a cached file does not contain valid JSON.
        FileNotFoundError: If the directory does not exist.
    """
    directory = cache_dir
    files = glob.glob(f"{directory}/*.json") 
    # Sort files by creation date
    files.sort(key=os.path.getctime)
    print('#======# Cached Files #======#')
    total_size = 0
    for index, file in enumerate(files):
        file_size = os.path.getsize(file)
        total_size += file_size
        with open(file, 'r') as f:
            data = json.load(f)
            sourcefile = data.get('sourcefile', 'N/A')
            date = data.get('date', 'N/A')
        print(f'[{index}] {os.path.basename(file)} ({file_size} bytes), Source file: {sourcefile}, Date created: {date}')
    total_size_mb = total_size / 1000000
    print(f'Total cache size: {total_size_mb:.2f} MB')
    print('Run "cache_clear()" to clear the cache')
    print('#============================#')



def Gamma2sigma(Gamma: float) -> float:
    """
    Converts Full Width at Half Maximum (FWHM) to standard deviation.

    This function is used for converting FWHM (Gamma) to standard deviation (sigma) for a normal distribution.

    Args:
        Gamma (float): The FWHM value.

    Returns:
        float: The standard deviation equivalent of the FWHM.
    """
    return Gamma * np.sqrt(2) / ( np.sqrt(2 * np.log(2)) * 2 )

def random_spectra(wavelength: np.ndarray, wavenumbers: bool = False) -> np.ndarray: 
    """
    Generates a random spectra for the scanned wavelength range.

    This function generates 5 peaks, though they may not be resolved. It's optimized for nm.

    Args:
        wavelength (np.ndarray): The scanned wavelength range.
        wavenumbers (bool, optional): If True, the function returns wavenumbers instead of wavelength. Defaults to False.

    Returns:
        np.ndarray: The total line spectrum in wavelength or wavenumbers.
    """
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

def fit_logger(result: dict) -> None:
    '''
    Sets up the data to be logged regarding the experiment, 'out' is the string to append to (with \n for a new line) 
    that will be written. Can add more things as we find the need. 

    Example: 
    --------
        >>> out += 'some data to add\n

    The save portion will try save to the specified directory, if it cant - it will attempt to dump it into the current working directory    
    '''
    data_path = os.path.abspath(os.getcwd())
   
    name = "0-fitlog" +'.pyet'
    name = name_checker((data_path + '/' + name))

    out ='%============================================%PYET fitting log%============================================%\n\n\n'

            
    out +='Date Start: '+ result['Initialised time'] + '\n'
    out +='Date Completed: '+ str(datetime.now()) + '\n'
    out += '\n\n'
    out += '%============================================%Fitting Configuration%============================================%\n\n\n'
    out += 'Solver parameters:' + "\n" + 'Solver: ' + str(result['solver']) + "\n" + 'Additional args:' + str(result['args'])  + "\n" + 'Additional kwargs:' + str(result['kwargs'])  + "\n\n"
    out += 'Number of free parameters: ' + str(len(result['guess'].keys())) + "\n\n"
    out += 'Free parameters:' + "\n" + '\n'.join(f"{k}" for k in result['guess'].keys()) + "\n\n"
    out += 'Initial guess:' + "\n" + '\n'.join(f"{k}: {v}" for k, v in result['guess'].items()) + "\n\n"
    out += 'Parameter bounds:' + "\n" + '\n'.join(f"{k}: {v}" for k, v in result['bounds'].items()) + "\n\n"
    out += 'Trace parameters:' + "\n" + '\n'.join(f"{k}: {v}" for k, v in result['Trace_info'].items()) + "\n\n"

    out += '%============================================%Fitting Result%============================================%\n\n\n'
    out += 'Fit Sucsessful?:' +  str(result['results']['success']) + "\n"
    out += result['results']['message'] + "\n" + "\n"
    out += 'Number of iterations:' +  str(result['results']['nfev']) + "\n"
    out += 'Fitted parameters:\n'
    for k in result['results']['x']:
        fitted_value = result['results']['x'][k]
        uncertainty_value = result['uncertainties'][k]
        out += f"{k}: {fitted_value} ± {uncertainty_value}\n\n"
    out += 'WRSS:' +  str(result['results']['fun']) + "\n"
    

    try:
        tfile = open(data_path  + '/' + name, 'a')
        tfile.write(out)
        tfile.close()
    except IOError as e:
        print('Directory doesnt exist!!')
        print('Saving to current working directory instead')
        pass
        try:
            data_path = os.path.abspath(os.getcwd())
            name = name_checker(data_path   + '/' + name)
            tfile = open(data_path  + '/' + name, 'a')
            tfile.write(out)
            tfile.close()
        except IOError as e:
            print(e) 
            print('Files failed to save')
            pass



def name_checker(fname_path):
    """
    Get the path to a filename which does not exist by incrementing path.
    """
    directory, filename = os.path.split(fname_path)
    if not os.path.exists(fname_path):
    
        return filename

    filename, file_extension = os.path.splitext(filename)
    prefix, name = filename.split('-', 1)
    i = int(prefix) if prefix.isdigit() else 0

    new_fname = "{}-{}{}".format(i, name, file_extension)

    while os.path.exists(os.path.join(directory, new_fname)):

        i += 1
        new_fname = "{}-{}{}".format(i, name, file_extension)
    return os.path.join(new_fname)


if __name__ == "__main__":
    
    cache_list()
    cache_clear()