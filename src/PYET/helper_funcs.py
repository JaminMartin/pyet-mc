import os
import sys
import json
import numpy as np
import glob
import plotly.graph_objs as go
import plotly.offline
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
import plotly.io as pio
from multiprocessing import Process
import tempfile
pio.templates.default = "none"

cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache'))
temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'temp'))
if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

def cleanup_temp_folder(temp_folder_path):
    for filename in os.listdir(temp_folder_path):
        if filename.endswith(".html"):
            file_path = os.path.join(temp_folder_path, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error while removing {file_path}: {e}")



def cache_writer(r, **params):

    file_name = f'{params["process"]}_{params["radius"]}_{params["concentration"]}_{params["interaction_type"]}_{params["iterations"]}'
    file_name = file_name.replace('.', 'pt')
    temp = {}
    temp['r_components'] = r.tolist()
    dictionary = params | temp
    with open(f'{cache_dir}/{file_name}.json', 'w') as fp:
        json.dump(dictionary, fp)
    
     

def cache_reader(**params):
    directory = cache_dir

    vmat = ([params["process"],str(params["radius"]),str(params["concentration"]),str(params["interaction_type"]),str(params["iterations"])])
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
        vmat = ([params["process"],str(params["radius"]),str(params["concentration"]),str(params["interaction_type"]),str(params["iterations"])])
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

def run_app(file_path):
    app = QApplication(sys.argv)
    web = QWebEngineView()
    web.load(QUrl.fromLocalFile(file_path))
    web.show()
    app.exec_()

#data structure for handling experimental data & radial info
class Trace:
    """
    The Trace class represents a trace of experimental data points, it allows provides some basic functionalaity to aid in plotting (through naming) and data parsing for manipulating in various ways prior to fitting.

    Attributes:
    trace (np.ndarray): The y-coordinates of the data points.
    name (str): The name of the trace.
    time (np.ndarray): The x-coordinates (time points) of the data points.
    radial_data (np.ndarray): The radial data associated with the trace, this would be pre-calculated based on the concentration of the sample.
    """
    def __init__(self, ydata: np.ndarray, xdata: np.ndarray, fname: str, radial_data: np.ndarray, parser = False):
        """
        The constructor for the Trace class.

        Parameters:
        ydata (np.ndarray): The y-coordinates of the data points.
        xdata (np.ndarray): The x-coordinates (time points) of the data points.
        fname (str): The name of the trace.
        radial_data (np.ndarray): The radial data associated with the trace, this would be pre-calculated based on the concentration of the sample.
        parser (bool, optional): A flag indicating whether to parse the trace data. Defaults to False.
        """
        self.trace = ydata
        self.name = fname
        self.time = xdata
        self.radial_data = radial_data
        if parser == True:
            self.trace = self.parse(self.trace)

        def parse(self, trace):
            print('not yet implemented')  


#TODO make this a standalone package
class Plot:
    def __init__(self, **layout_kwargs):
        self.fig = go.Figure()
        self.plot_type = 'default'
        #these are not currently initialised as they need some refining
        # TODO find some good defaults & window size for plots that couple well to plotting & saving for standard journal formats. 
        self.default_layout = {
            'title_text': "",
            'margin': dict(l=35, r=35, t=35, b=35),
            'paper_bgcolor': "white",
            'showlegend': True,
            'title': '',
            'font': dict(family='Times New Roman, monospace', size=20, color='black'),
            'xaxis': dict(
                title='',
                exponentformat='none',
                showgrid=False,
                showline=True,
                tickmode='linear',
                ticks='outside',
                dtick=50,
                showticklabels=False,
                linewidth=4, linecolor='black',
                ticklen=7.5,
                tickwidth=4,
                tickcolor='black',
                tickfont=dict(
                    family='Times new roman, monospace',
                    size=20,
                    color='black'),
                titlefont=dict(
                    family='Times new roman, monospace',
                    size=20,
                    color='black',
                )
            ),
            'yaxis': dict(
                title='Intensity (arb. units.)',
                exponentformat='none',
                showgrid=False,
                zeroline=False,
                showline=True,
                ticks='',
                tickmode='linear',
                dtick=10,
                ticklen=15,
                tickwidth=4,
                showticklabels=False,
                linewidth=4, linecolor='black',
                titlefont=dict(
                    family='Times new roman, monospace',
                    size=20,
                    color='black')
            )
        } 
        self.default_layout.update(layout_kwargs)
        self.default_transient_layout = {
            'title_text': "",
            'font': dict(family='Times New Roman, monospace', size=20, color='black'),
            'xaxis': dict(
                title='Time (ms)',
                exponentformat='none',
                showgrid=False,
                showline=True,
                zeroline=False,
                range=[0,0.01],
                tickmode='linear',
                ticks='outside',
                tick0=0,
                dtick=0.01,
                linewidth=4, linecolor='black',
                ticklen=15,
                tickwidth=4,
                tickcolor='black',
                tickfont=dict(
                    family='Times new roman, monospace',
                    size=20,
                    color='black'),
                titlefont=dict(
                    family='Times new roman, monospace',
                    size=20,
                    color='black')
            ),
            'yaxis': dict(
                title='Intensity (arb. units.)',
                exponentformat='none',
                showgrid=False,
                zeroline=False,
                showline=True,
                ticks='',
                #range=[np.log(0.015), np.log(1)],
                showticklabels=False,
                linewidth=4, linecolor='black',
                titlefont=dict(
                    family='Times new roman, monospace',
                    size=20,
                    color='black')
            )
        }
        self.default_layout.update(layout_kwargs)


    def scatter_xy(self, x, y, *args, **kwargs):
        # Set default scatter trace options
        default_trace_options = {
            'mode': 'lines',
            }

        
        trace_options = {**default_trace_options, **kwargs}
        trace = go.Scatter(x=x, y=y, *args, **trace_options)
        self.fig.add_trace(trace)


    def transient(self, x, y=None, fit=False, *args, **kwargs):
        self.plot_type = 'transient'
        if fit:
            default_trace_options = {'mode': 'lines'}
        else:
            default_trace_options = {'mode': 'markers'}

        trace_options = {**default_trace_options, **kwargs}

        # Check if x is a Trace instance
        if isinstance(x, Trace):
            trace = go.Scatter(x=x.time, y=x.trace, name=x.name, *args, **trace_options)
        else:
            trace = go.Scatter(x=x, y=y, *args, **trace_options)

        self.fig.add_trace(trace)

    def cleanup_temp_file(self):
        if hasattr(self, 'temp_file_path'):
            os.remove(self.temp_file_path)

    def show(self):
        if self.plot_type == 'default':
            # Set default layout options
            self.fig.update_layout(**self.default_layout)
        elif self.plot_type == 'transient':
            self.fig.update_layout(**self.default_transient_layout) 
            self.fig.update_yaxes(type="log")   
        else:
            print('invalid plot type, defaulting to default')  
            self.fig.update_layout(**self.default_layout)  

        with tempfile.NamedTemporaryFile(suffix=".html", dir=temp_dir, delete=False) as temp:
            plotly.offline.plot(self.fig, filename=temp.name, auto_open=False)
            self.temp_file_path = os.path.abspath(temp.name)
            self.process = Process(target=run_app, args=(self.temp_file_path,))
            self.process.start()

    def __del__(self):
        self.cleanup_temp_file()

    
     
    #TODO add figure saving 



if __name__ == "__main__":
    #data = cache_reader(process = 'singlecross', radius = 10 , concentration = 2.5 , iterations = 50000 , interaction_type = 'QQ')
    cache_list()
    #cache_clear()    
    x = [0,2,3,4,6,7,8,9,10]
    y = [11,12,13,14,15,16,17,18,19 ]
    x2 = [5,6,74,8,99,83,91,100]
    y2 = [11,12,13,14,15,16,17,18,19 ]
    figure = Plot()
    figure.transient(x,y)
    figure.transient(x2,y2)
    figure.show()




    figure2 = Plot()
    figure2.transient(x2,y2, fit = True)
    figure2.show()