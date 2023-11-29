import plotly.graph_objs as go
import plotly.offline
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
import plotly.io as pio
from multiprocessing import Process
import tempfile
pio.templates.default = "none"
import toml
import pkg_resources
import os
import sys
import numpy as np
from .pyet_utils import Trace

config_file = pkg_resources.resource_filename(__name__, 'plotting_config/plotting_config.toml')

with open(config_file, "r") as f:
    config = toml.load(f)


def run_app(file_path):
    app = QApplication(sys.argv)
    web = QWebEngineView()
    web.load(QUrl.fromLocalFile(file_path))
    web.show()
    app.exec_()


class Plot:
    def __init__(self, **layout_kwargs):
        self.fig = go.Figure()
        self.plot_type = 'default'
        self.default_layout = dict(config.get("default_layout", {}))  # Create a new dictionary
        self.default_layout.update(layout_kwargs)
        self.default_transient_layout = dict(config.get("transient_layout", {}))
        self.default_transient_layout.update(layout_kwargs)
        
        # Update any specified keys in the default layout with the provided values
        for key, value in layout_kwargs.items():
            if key in self.default_layout:
                self.default_layout[key].update(value)
            else:
                self.default_layout[key] = value
        
        for key, value in layout_kwargs.items():
            if key in self.default_transient_layout:
                self.default_transient_layout[key].update(value)
            else:
                self.default_transient_layout[key] = value

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


    def calculate_nice_round_number(self, value):
        # Find a nice round number or factor of value
        nice_round_numbers = [0.01, 0.02, 0.05, 0.1, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]  # You can extend this list with more nice round numbers
        for nice_number in nice_round_numbers:
            if value / nice_number <= 5:  # Adjust the threshold as needed
                return nice_number

        # If no suitable nice round number is found, return a fallback value
        return 1
    
    def update_layout_bounds(self):
        x_max, y_max = float('-inf'), float('-inf')

        for trace in self.fig.data:
            # Check if x is not empty or None
            if trace.x is not None and len(trace.x) > 0:
                # Update x-axis bounds
                x_max = max(x_max, max(trace.x))

            # Check if y is not empty or None
            if trace.y is not None and len(trace.y) > 0:
                # Update y-axis bounds
                y_max = max(y_max, max(trace.y))

    
        t_max = x_max
        t_min = 0
        y_max = 1
        y_min = 0.1 * y_max
                
        self.default_transient_layout['yaxis']['range'] = [np.log(y_min), np.log(y_max)]
        self.default_transient_layout['xaxis']['range'] = [t_min, t_max]
        
        t_range = t_max - t_min
        dtick = self.calculate_nice_round_number(t_range)
        self.default_transient_layout['xaxis']['dtick'] = dtick
        



    def show(self):
        if self.plot_type == 'default':
            # Set default layout options
            self.fig.update_layout(**self.default_layout)
        elif self.plot_type == 'transient':
            self.update_layout_bounds()
            self.fig.update_layout(**self.default_transient_layout) 
            self.fig.update_yaxes(type="log")   
        else:
            print('invalid plot type, defaulting to default')  
            self.fig.update_layout(**self.default_layout)

    
        # Use the system's temporary directory
        temp_dir = tempfile.gettempdir()
        print(f"Temporary directory for debugging: {temp_dir}")

        # Use NamedTemporaryFile to create a temporary file in the system's temp directory
        with tempfile.NamedTemporaryFile(suffix=".html", dir=temp_dir, delete=False) as temp:
            self.temp_file_path = os.path.abspath(temp.name)
            plotly.offline.plot(self.fig, filename=self.temp_file_path, auto_open=False)

            # Start the process using self.temp_file_path
            self.process = Process(target=run_app, args=(self.temp_file_path,))
            self.process.start()

    #First layer temp file clean up (as these can be quite large) system level clean up handles any python process / garbage collection failure at reboot (rarely needed)
    def __del__(self):
        self.cleanup_temp_file()

    def cleanup_temp_file(self):
        if hasattr(self, 'temp_file_path') and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    #TODO add figure saving 


if __name__ == "__main__":
    
     
    x = [0,2,3,4,6,7,8,9,10]
    y = [11,12,13,14,15,16,17,18,19 ]
    x2 = [5,6,74,8,99,83,91,100]
    y2 = [11,12,13,14,15,16,17,18,19 ]
    # Example usage
    x_range = [0,50]
    y_range = [0,100]
    margins = {'l': 100, 'r': 100, 't': 100, 'b': 100}
    figure = Plot(xaxis={'range': x_range, 'dtick': 50}, yaxis={'range': y_range}, margin=margins)
    print(f"Figure 1 Plot Type: {figure.plot_type}")
    figure.scatter_xy(x, y)
    figure.show()

    figure2 = Plot()
    print(f"Figure 2 Plot Type: {figure2.plot_type}")
    figure2.scatter_xy(x2, y2)
    figure2.show()