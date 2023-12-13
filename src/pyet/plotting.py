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
from .pyet_utils import Trace , random_spectra
import copy
from typing import Union

config_file = pkg_resources.resource_filename(__name__, 'plotting_config/plotting_config.toml')

with open(config_file, "r") as f:
    config = toml.load(f)


def run_app(file_path: str) -> None:
    """
    Run a Qt application to display a web page from a local file.

    This function creates a QApplication and a QWebEngineView, loads the web page from the specified local file into the QWebEngineView, shows the QWebEngineView, and then starts the QApplication event loop.

    Parameters:
        file_path (str): The path to the local file to display in the QWebEngineView.

    Returns:
        None
    """
    app = QApplication(sys.argv)
    web = QWebEngineView()
    web.load(QUrl.fromLocalFile(file_path))
    web.show()
    app.exec_()

def load_local_config(local_config_path: str) -> None:
    """
    Load a local configuration file and overwrite the default configuration.

    Parameters:
    local_config_path (str): The path to the local configuration file.
    """

    # Load the local configuration file
    local_config = toml.load(local_config_path)

    # Update the default configuration with the local configuration
    config.update(local_config)


class Plot:
    """
    A class used to represent a Plot.

    This class creates a plot figure and sets default layouts for different types of plots. 
    It also updates these default layouts with any provided layout keyword arguments.

    Attributes:
        fig (Figure): The plot figure.
        plot_type (str): The type of the plot. Default is 'default'.
        default_spectra_layout (dict): The default layout for the plot.
        default_transient_layout (dict): The default layout for a transient plot.
        default_structure3d_layout (dict): The default layout for a 3D scatter plot.
        layout (dict): The layout keyword arguments provided when initializing the class.

    Methods:
        __init__(self, **layout_kwargs): Initializes the Plot class and updates the default layouts with any provided layout keyword arguments.
        spectra(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list], *args, **plotting_kwargs): Creates a scatter plot with the given x and y data.
        transient(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list, None] = None, fit: bool =False, *args, **plotting_kwargs): Creates a transient plot with the given x and y data.
        structure_3d(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list], z: Union[np.ndarray, list], *args, **plotting_kwargs): Creates a 3D scatter plot with the given x, y, and z data.
        calculate_nice_round_number(self, value: Union[float, int]): Calculates a nice round number that is a factor of the given value.
        update_layout_bounds(self): Updates the layout bounds of the figure.
        show(self): Displays the figure based on the plot type.
        save(self, path: str, name: str): Saves the figure to a specified location.
        __del__(self): Cleans up the temporary file created for the plot.
        cleanup_temp_file(self): Removes the temporary file created for the plot if it exists.
    """
    def __init__(self, **layout_kwargs):
        """
        Initializes the Plot class and updates the default layouts with any provided layout keyword arguments.

        Parameters:
            **layout_kwargs: Arbitrary keyword arguments to update the default layouts.
        """
        self.fig = go.Figure()
        self.plot_type = 'default'
        self.default_spectra_layout = copy.deepcopy(config.get("spectra_layout", {}))
        self.default_transient_layout = copy.deepcopy(config.get("transient_layout", {}))
        self.default_structure3d_layout = copy.deepcopy(config.get("structure_3d_layout", {}))
            
        self.layout = layout_kwargs


        # Update any specified keys in the default layout with the provided values
        for key, value in layout_kwargs.items():
            if key in self.default_spectra_layout:
                self.default_spectra_layout[key].update(value)
            else:
                self.default_spectra_layout[key] = value
        
            if key in self.default_transient_layout:
                self.default_transient_layout[key].update(value)
            else:
                self.default_transient_layout[key] = value

            if key in self.default_structure3d_layout:
                self.default_structure3d_layout[key].update(value)
            else:
                self.default_structure3d_layout[key] = value
      

    def spectra(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list], *args, **plotting_kwargs) -> None:
        """
        Create a scatter plot with the given x and y data.

        The function sets default trace options for a scatter plot and then updates these options with any provided in plotting_kwargs.

        A scatter trace is created with the x and y data and the trace options, and this trace is added to the figure.

        Parameters:
            x (Union[np.ndarray, list]): The x data for the scatter plot.
            y (Union[np.ndarray, list]): The y data for the scatter plot.
            *args: Variable length argument list.
            **plotting_kwargs: Arbitrary keyword arguments to update the default trace options.

        Returns:
            None
        """
        # Set default scatter trace options
        default_trace_options = {
            'mode': 'lines',
            'line': {
        'color': 'black',  
        'width': 3  
    }}
        
        for key, value in plotting_kwargs.items():
            if key in default_trace_options:
                default_trace_options[key].update(value)
            else:
                default_trace_options[key] = value
       
        trace = go.Scatter(x=x, y=y, *args, **default_trace_options)
        self.fig.add_trace(trace)


    def transient(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list, None] = None, fit: bool =False, *args, **plotting_kwargs) -> None:
        """
        Create a transient plot with the given x and y data.

        The function sets the plot type to 'transient' and defines default trace options based on the fit parameter. 
        It then updates these options with any provided in plotting_kwargs.

        If x is an instance of Trace, a scatter trace is created with the time and trace data from x and the trace options.
        Otherwise, a scatter trace is created with the x and y data and the trace options. 
        This trace is then added to the figure.

        Parameters:
            x (Union[np.ndarray, list]): The x data for the scatter plot, or a Trace instance.
            y (Union[np.ndarray, list, None]): The y data for the scatter plot. Ignored if x is a Trace instance.
            fit (bool): If True, the trace mode is set to 'lines'. Otherwise, it's set to 'markers'.
            *args: Variable length argument list.
            **plotting_kwargs: Arbitrary keyword arguments to update the default trace options.

        Returns:
            None
        """
        self.plot_type = 'transient'
        if fit:
            default_trace_options = {'mode': 'lines'}
        else:
            default_trace_options = {'mode': 'markers'}

        for key, value in plotting_kwargs.items():
            if key in default_trace_options:
                default_trace_options[key].update(value)
            else:
                default_trace_options[key] = value

        # Check if x is a Trace instance
        if isinstance(x, Trace):
            trace = go.Scatter(x=x.time, y=x.trace, name=x.name, *args, **default_trace_options)

        else:
            trace = go.Scatter(x=x, y=y, *args, **default_trace_options)
        self.fig.add_trace(trace)

    def structure_3d(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list], z: Union[np.ndarray, list], *args, **plotting_kwargs) -> None:

        """
        Create a 3D scatter plot with the given x, y, and z data.

        The function sets the plot type to 'structure_3d' and defines default trace options. 
        It then updates these options with any provided in plotting_kwargs.

        A 3D scatter trace is created with the x, y, and z data and the trace options, 
        and this trace is added to the figure.

        Parameters:
            x (Union[np.ndarray, list]): The x data for the scatter plot.
            y (Union[np.ndarray, list]): The y data for the scatter plot.
            z (Union[np.ndarray, list]): The z data for the scatter plot.
            *args: Variable length argument list.
            *plotting_kwargs: Keyword arguments to update the default trace options.

        Returns:
            None
        """
        self.plot_type = 'structure_3d'
        default_trace_options = {
            'mode': 'markers',
            'marker': {
                'size': 10
            }
        }
        for key, value in plotting_kwargs.items():
            if key in default_trace_options:
                default_trace_options[key].update(value)
            else:
                default_trace_options[key] = value
        
        trace = go.Scatter3d(x=x, y=y, z=z, *args, **default_trace_options)
        self.fig.add_trace(trace)

    def calculate_nice_round_number(self, value: Union[float, int]) -> Union[float,int]:
        """
        Calculate a nice round number that is a factor of the given value.

        This function iterates over a list of nice round numbers. If the given value divided by a nice round number is less than or equal to 5, 
        that nice round number is returned.

        If no suitable nice round number is found, the function returns a fallback value of 1.

        Parameters:
            value (Union[float, int]): The value for which to find a nice round number.

        Returns:
            Union[float, int]: A nice round number that is a factor of the given value, or 1 if no suitable number is found.
        """
        nice_round_numbers = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]  # You can extend this list with more nice round numbers
        for nice_number in nice_round_numbers:
            if value / nice_number <= 5:  # Adjust the threshold as needed
                return nice_number

        # If no suitable nice round number is found, return a fallback value
        return 1
    
    def update_layout_bounds(self) -> None:
        """
        Update the layout bounds of the figure.

        This function iterates over the data in the figure. If the x and y data are not empty or None, 
        it updates the x and y-axis bounds. 

        If the 'xaxis' or 'yaxis' range and 'xaxis' dtick are not set in the layout, 
        it updates them in the default and transient layouts.

        Returns:
            None
        """

        x_min, x_max = float('inf'), float('-inf')
        y_min, y_max = float('inf'), float('-inf')
        z_min, z_max = float('inf'), float('-inf')
        for trace in self.fig.data:
            # Check if x is not empty or None
            if trace.x is not None and len(trace.x) > 0:
                # Update x-axis bounds
                x_min = min(x_min, min(trace.x))
                x_max = max(x_max, max(trace.x))

            # Check if y is not empty or None
            if trace.y is not None and len(trace.y) > 0:
                # Update y-axis bounds
                y_min = min(y_min, min(trace.y))
                y_max = max(y_max, max(trace.y))
            
                # Only update the layout bounds if they are not set in layout_kwargs
            if 'xaxis' not in self.layout or 'range' not in self.layout['xaxis']:
                self.default_transient_layout['xaxis']['range'] = [0, x_max]
                self.default_spectra_layout['xaxis']['range'] = [x_min, x_max]
                #self.default_structure3d_layout['scene']['xaxis']['range'] = [x_min-10, x_max+10]
            if 'yaxis' not in self.layout or 'range' not in self.layout['yaxis']:
                self.default_transient_layout['yaxis']['range'] = [np.log(0.1), np.log(1)]
                #self.default_structure3d_layout['scene']['yaxis']['range'] = [y_min-10, y_max+10]
            #if 'zaxis' not in self.layout or 'range' not in self.layout['zaxis']:
                #self.default_structure3d_layout['scene']['zaxis']['range'] = [z_min-10, z_max+10]
            if 'xaxis' not in self.layout or 'dtick' not in self.layout['xaxis']:
                x_range = x_max - x_min
                dtick = self.calculate_nice_round_number(x_range)
                self.default_transient_layout['xaxis']['dtick'] = dtick
                self.default_spectra_layout['xaxis']['dtick'] = dtick    


    def show(self):
        """
        Display the figure based on the plot type.

        If the plot type is 'default' or 'transient', the layout bounds are updated before displaying only if they are not explicitly over written in the config.toml or passed to Plot() when itinitalising the class. 
        If the plot type is 'structure_3d', the 3D scatter layout is used.
        If the plot type is not recognized, it defaults to 'default'.

        The figure is saved as a temporary HTML file in the system's temporary directory, and a new QT5 webegine process is started to display it.

        Returns:
            None
        """
        if self.plot_type == 'default':
            # Set default layout options
            self.update_layout_bounds()
            self.fig.update_layout(**self.default_spectra_layout)

        elif self.plot_type == 'transient':
            self.update_layout_bounds()
            self.fig.update_layout(**self.default_transient_layout) 
            self.fig.update_yaxes(type="log")  

        elif self.plot_type == 'structure_3d':  
            #self.update_layout_bounds()
            self.fig.update_layout(**self.default_structure3d_layout)
        else:
            print('invalid plot type, defaulting to default')  
            self.fig.update_layout(**self.default_spectra_layout)

    
        # Use the system's temporary directory
        temp_dir = tempfile.gettempdir()
        #print(f"Temporary directory for debugging: {temp_dir}")
        
        # Use NamedTemporaryFile to create a temporary file in the system's temp directory
        with tempfile.NamedTemporaryFile(suffix=".html", dir=temp_dir, delete=False) as temp:
            self.temp_file_path = os.path.abspath(temp.name)
            plotly.offline.plot(self.fig, filename=self.temp_file_path, auto_open=False)

            # Start the process using self.temp_file_path
            self.process = Process(target=run_app, args=(self.temp_file_path,))
            self.process.start()

    def save(self, path: str, name: str) -> None:
        """
        Save the figure to a specified location.

        Parameters:
            path (str): The directory where the figure should be saved.
            name (str): The name of the file (including extension e.g. .svg) to save the figure as.

        Returns:
        None
        """
        directory_withname = os.path.join(path, name)
        self.fig.write_image(directory_withname)


    #First layer temp file clean up (as these can be quite large) system level clean up handles any python process / garbage collection failure at reboot (rarely needed)
    def __del__(self):
        self.cleanup_temp_file()

    def cleanup_temp_file(self):
        if hasattr(self, 'temp_file_path') and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    
        

if __name__ == "__main__":
    margins = {'l': 30, 'r': 0, 't': 30, 'b': 30}
    figure = Plot(margin = margins)
    
    figure.structure_3d([0,1,2],[0,5,2],[0,1,5])
    figure.structure_3d([5,1,1],[2,0,1],[2,2,1], name='yttrium', marker={'size': 10})
    figure.show()
    # margins = {'l': 30, 'r': 0, 't': 30, 'b': 30} 
    # x = [0,2,3,4,6,7,8,9,10]
    # y = [11,12,13,14,15,16,17,18,19]
    # x2 = [5,6,74,8,99,83,91,100]
    # y2 = [11,12,13,14,15,16,17,18,19]
    # # # Example usage
    # x_range = [0,50]
    # y_range = [0,1000]
    # margins = {'l': 100, 'r': 100, 't': 100, 'b': 100}
    # figure2= Plot(xaxis={'range': x_range, 'dtick': 50}, yaxis={'range': y_range}, margin=margins)
    # figure2.spectra(x, y, name = 'an example')
    # figure2.show()

    load_local_config('/Users/jamin/Documents/local_plotting_config.toml')
    wavelengths = np.arange(400,450, 0.1) #generate some values between 400 and 450 nm
    wavenumbers, signal = random_spectra(wavelengths, wavenumbers=True)
    figure1 = Plot()
    figure1.spectra(wavenumbers, signal, name = 'an example') #give the data a name for the legend
    figure1.show()
    path = '/Users/jamin/Documents/'
    name = 'temp2.svg'
    figure1.save(path, name)
