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


#TODO make this a standalone package
class Plot:
    def __init__(self, **layout_kwargs):
        self.fig = go.Figure()
        #these are not currently initialised as they need some refining
        # TODO find some good defaults & window size for plots that couple well to plotting & saving for standard journal formats. 
        # self.default_layout = {
        #     'title_text': "",
        #     'margin': dict(l=35, r=35, t=35, b=35),
        #     'paper_bgcolor': "white",
        #     'showlegend': False,
            # 'title': '',
            # 'font': dict(family='Times New Roman, monospace', size=20, color='black'),
            # 'xaxis': dict(
            #     title='',
            #     exponentformat='none',
            #     showgrid=False,
            #     showline=True,
            #     tickmode='linear',
            #     ticks='outside',
            #     dtick=50,
            #     showticklabels=False,
            #     linewidth=4, linecolor='black',
            #     ticklen=7.5,
            #     tickwidth=4,
            #     tickcolor='black',
            #     tickfont=dict(
            #         family='Times new roman, monospace',
            #         size=20,
            #         color='black'),
            #     titlefont=dict(
            #         family='Times new roman, monospace',
            #         size=20,
            #         color='black',
            #     )
            # ),
        #     'yaxis': dict(
        #         title='Intensity (arb. units.)',
        #         exponentformat='none',
        #         showgrid=False,
        #         zeroline=False,
        #         showline=True,
        #         ticks='',
        #         tickmode='linear',
        #         dtick=10,
        #         ticklen=15,
        #         tickwidth=4,
        #         showticklabels=False,
        #         linewidth=4, linecolor='black',
        #         titlefont=dict(
        #             family='Times new roman, monospace',
        #             size=20,
        #             color='black')
        #     )
        # }
        self.default_layout = {} 
        self.default_layout.update(layout_kwargs)

    def scatter_xy(self, x, y, *args, **kwargs):
        # Set default scatter trace options
        default_trace_options = {
            'mode': 'lines',
            }

        
        trace_options = {**default_trace_options, **kwargs}
        trace = go.Scatter(x=x, y=y, *args, **trace_options)
        self.fig.add_trace(trace)


    def show(self):
        # Set default layout options
        self.fig.update_layout(**self.default_layout)

        with tempfile.NamedTemporaryFile(suffix=".html", dir=temp_dir, delete=False) as temp:
            plotly.offline.plot(self.fig, filename=temp.name, auto_open=False)
            self.temp_file_path = os.path.abspath(temp.name)
            self.process = Process(target=run_app, args=(self.temp_file_path,))
            self.process.start()

    def __del__(self):
        if hasattr(self, 'temp_file_path'):
            os.remove(self.temp_file_path)

    
     
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
    figure.scatter_xy(x,y)
    figure.scatter_xy(x2,y2)
    figure.show()




    figure2 = Plot()
    figure2.scatter_xy(x2,y2)
    figure2.show()