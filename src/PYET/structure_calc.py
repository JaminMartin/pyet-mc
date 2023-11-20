import numpy as np
import numpy.linalg as LA
from pymatgen.io.cif import CifParser
import matplotlib.pyplot as plt
import pandas as pd
from . import helper_funcs 
import os
from typing import Union, Optional, List

class Structure:
    '''
    A class for handling the structural info of a host crystal. A central ion, e.g. a Ytrrium ion must be specified for the associated methods to work. Once this ion has been specified the nearest neigbour ions can be calculated. This can either return cartesian or spherical polar coordinates for further calculations or plotting. There is also a simple function for printing off this information for a quick analyis. Lastly this class provides plotting functionality directly for visualisation purposes. 

    Methods:
    __init__(self, cif_file): Initializes the Structure using a CIF file.
    centre_ion(self,ion): Identifies the index of a specified ion in the structure.
    nearest_neighbours_info(self, radius): Prints the species and radial distance of the neighbors within a specified radius of the central ion.
    nearest_neighbours_coords(self, radius): Returns the coordinates of the neighbors within a specified radius of the central ion in x,y,z coords. 
    nearest_neighbours_spherical_coords(self,radius): Returns the coordinates of the neighbors within a specified radius of the central ion in spherical coords. 
    structure_plot(self, radius, filter = None): Generates a 3D plot of the structure.
    """
    '''
    def __init__(self,cif_file: str):
        """
        Initializes the Structure object with a CIF file.

        Parameters:
        cif_file (str): The path to the CIF file to parse.

        Sets:
        self.cif (CifParser): The CifParser object for the CIF file.
        self.struct (Structure): The first structure from the parsed CIF file.

        Raises:
        Exception: If the CIF file is invalid or not provided.
        """
        try:
            self.cif = CifParser(cif_file)
            self.struct = self.cif.get_structures()[0]
        except:
            print('Invalid or no CIF file provided')
          
    def centre_ion(self,ion: str) -> None:
        """
        Identifies the index of a specified ion in the structure.

        Parameters:
        ion (str): The ion to find, e.g. "Y".

        Sets:
        self.ion_index (int): The index of the ion in the structure.
        self.site (Site): The site of the ion in the structure.
        self.centre_ion_species (str): The species of the ion.
        self.origin (array): The coordinates of the ion.
        """
        structure_sites = self.struct.sites
        for i in range(len(structure_sites)):
            temp = structure_sites[i]
            if temp.species_string == ion:
                self.ion_index = i
                self.site = self.struct.sites[self.ion_index] #22 ky3f10 8 K2YF5 10 LiYF4 4 NaYF
                self.centre_ion_species = self.site.species_string  
                self.origin = self.site.coords
                break
            
            else:
                pass    
        
    def nearest_neighbours_info(self, radius: float) -> None: 
        """
        Prints the species and radial distance of the neighbors within a specified radius of the central ion.

        Parameters:
        radius (float/int): The radius within which to find neighbors.

        Sets:
        self.nn (list): The list of neighbors within the specified radius.

        Prints:
        A formatted string with the species and radial distance of each neighbor.
        """
        self.nn = self.struct.get_neighbors(self.site, radius)
        s = ""
        heading = f"Nearest neighbours within radius {radius} Angstroms of a {self.centre_ion_species} ion:\n"
        s += (heading)
        for n in self.nn:
            s += "Species = %s, r = %f Angstrom\n" % (n[0].species.chemical_system, self.site.distance(n[0]))
        s += "\n"
        print(s)

    def nearest_neighbours_coords(self, radius: float) -> pd.DataFrame: 
        """
        Returns the coordinates of the neighbors within a specified radius of the central ion in cartesian coordinates .

        Parameters:
        radius (float/int): The radius within which to find neighbors.

        Returns:
        DataFrame: A DataFrame with columns 'x', 'y', 'z', and 'species', containing the cartesian coordinates coordinates and species of ions within radius r.
        """ 
        NN = self.struct.get_neighbors(self.site, radius)
        XYZ = np.zeros([len(NN), 3])
        Species_info = []
        for i,N in enumerate(NN):
            xyz = N[0].coords
            XYZ[i, 0] = xyz[0]
            XYZ[i, 1] = xyz[1]
            XYZ[i, 2] = xyz[2]
            Species_info.append(NN[i].species_string )
        
        Species_info = pd.DataFrame(np.asarray(Species_info), columns= ['species'])
        coordinate_df = pd.DataFrame(XYZ, columns=['x', 'y', 'z'])
        nearest_neigbours = pd.concat([coordinate_df, Species_info],axis=1)
        return nearest_neigbours   
    
    def nearest_neighbours_spherical_coords(self,radius: float) -> pd.DataFrame: 
        """
        Returns the coordinates of the neighbors within a specified radius of the central ion in .

        Parameters:
        radius (float/int): The radius within which to find neighbors.

        Returns:
        DataFrame: A DataFrame with columns 'x', 'y', 'z', and 'species', containing the spherical coordinates coordinates and species of ions within radius r.
        """      
        NN = self.struct.get_neighbors(self.site, radius)
        
        spc = np.zeros([len(NN), 3])
        Species_info = []
        for i,N in enumerate(NN):
            xyz = N[0].coords-self.origin
            spc[i, 0] = LA.norm(xyz)
            spc[i, 1] = 180/(np.pi) * (np.arccos(xyz[2]/spc[i,0]))
            spc[i, 2] = 180/(np.pi) * (np.arctan2(xyz[1],xyz[0]))
            Species_info.append(NN[i].species_string )

        Species_info = pd.DataFrame(np.asarray(Species_info), columns= ['species'])
        coordinate_df = pd.DataFrame(spc, columns=['r', 'theta', 'phi'])
        nearest_neigbours = pd.concat([coordinate_df, Species_info],axis=1)
        return nearest_neigbours
    
    def structure_plot(self, radius: float, filter: Optional[List[str]] = None, blocking: Optional[bool] = True) -> Union[None, Exception]:
        """
        Renders a 3D plot of a given radius around the central ion. A filter can be provided to only plot certain species.

        Parameters:
        radius (float/int): The radius within which to plot neighbors.
        filter (list, optional): A list of species to plot. If not provided, all species are plotted.
        blocking (bool, optional): Sets if the plotting is blocking or not, this is used for testing purposes
        Returns:
        None. The function directly plots the 3D structure using matplotlib.
        """
        coords_xyz = self.nearest_neighbours_coords(radius)
        UniqueNames = coords_xyz.species.unique()

        DataFrameDict = {elem : pd.DataFrame() for elem in UniqueNames}
        for key in DataFrameDict.keys():
            DataFrameDict[key] = coords_xyz[:][coords_xyz.species == key]
        
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d') 
        ax.scatter(self.origin[0] ,self.origin[1] ,self.origin[2], label=f'central {self.centre_ion_species} ion')
        ax.set_xlabel('X (Angstrom)')
        ax.set_ylabel('Y (Angstrom)')
        ax.set_zlabel('Z (Angstrom)')

        if filter is not None:
            if not isinstance(filter, list):
                raise TypeError('Filter must be a list of strings.')
            if not all(isinstance(item, str) for item in filter):
                raise TypeError('All elements in the filter list must be strings.')
            if any(item not in DataFrameDict for item in filter):
                raise KeyError('Some elements in the filter list are not keys of the DataFrame.')
            

        if filter == None:
            for i in range(len(UniqueNames)):
                temp = DataFrameDict[UniqueNames[i]]
                ax.scatter(temp.x, temp.y, temp.z, label=UniqueNames[i])
            ax.legend()  
            plt.show(block=blocking)  # Ensure plt.show() is called without block parameter
            self.fig = plt.gcf()     
        else:
         
            for i in range(len(filter)):
                temp = DataFrameDict[filter[i]] 
                ax.scatter(temp.x, temp.y, temp.z, label=filter[i])   
            ax.legend()  
            plt.show(block=blocking)  # Ensure plt.show() is called without block parameter
            self.fig = plt.gcf()



   
class Interaction:
        """
        Represents an interaction within a given Structure instance.

        The Interaction class inherits the attributes of the Structure class and provides additional methods to simulate distances and interactions.

        Attributes:
        structure (Structure): An instance of the Structure class.

        Methods:
        __init__(self, Structure): Initializes the Interaction with a Structure instance.
        distance_sim(self, radius, concentration, dopant): Simulates and returns the distances to a specified dopant within a given radius.
        sim_single_cross(self, radius, concentration, iterations, interaction_type): Simulates a single cross-relaxation interaction within a given radius.
        distplot_summary(self, radius, concentration, dopant = 'acceptor', filter = None): Generates a 3D plot of the structure including dopant ions.
        """
        def __init__(self, structure: Structure):
            """
            Initializes the Interaction with a Structure instance.

            Parameters:
            Structure (Structure): An instance of the Structure class.

            Sets:
            self.structure (Structure): The Structure instance.

            Prints:
            The species of the central ion in the Structure instance, or an error message if the Structure instance or the central ion is not specified.
            """
            try:
                self.structure = structure
                print(f' Central ion is {self.structure.centre_ion_species}')
            except:
                print('Either structure or central ion is not specified')  
       

        
        def distance_sim(self, radius: float, concentration: float, dopant: Optional[str] = 'acceptor') -> np.ndarray:
            """
            Simulates and returns the distances to a specified (but randomly created based on concentration) dopant within a given radius to the central ion.

            Parameters:
            radius (float/int): The radius within which to simulate distances.
            concentration (float): The concentration of the dopant in %.
            dopant (str, optional): The type of dopant. Defaults to 'acceptor'.

            Returns:
            numpy.ndarray: An array of distances to the dopant.
            """
            concentration = concentration / 100
            
            coords = self.structure.nearest_neighbours_spherical_coords(radius)
            self.filtered_coords = coords.loc[coords['species'].isin([self.structure.centre_ion_species])].reset_index(drop=True)
            
       
            for i in self.filtered_coords.index:
                if np.random.rand() < concentration:
                    self.filtered_coords.loc[i, 'species'] = dopant
            
            distances = self.filtered_coords.loc[self.filtered_coords['species'].isin([dopant])].reset_index(drop=True)
            distances = distances['r'].to_numpy()
            return distances
        
        def sim_single_cross(self, radius: float, concentration: float, iterations: int, interaction_type: Optional[str] = None) -> Union[float, Exception]:
            """
            Simulates a single cross-relaxation interaction within a given radius.

            Parameters:
            radius (float/int): The radius within which to simulate interactions.
            concentration (float): The concentration of the dopant.
            iterations (int): The number of iterations to run the simulation.
            interaction_type (str): The type of interaction. Can be 'DD', 'DQ', or 'QQ'. This must be set.

            Returns:
            float: The average of r_i, which represents the simulated interaction.
            """
            process = 'singlecross'
            cache_data = helper_funcs.cache_reader(process = process, radius = radius, concentration = concentration, iterations = iterations, interaction_type = interaction_type)
            match cache_data: 
                case None:
                    print('Simulator: File not found in cache, running simulation')
                    match interaction_type:
                        case 'DD':
                            s = 6
                        case 'DQ':     
                            s = 8
                        case 'QQ':
                            s = 10   
                        case _ :
                            raise ValueError("Please specify interaction type")  
                        
                    r_i = np.zeros(iterations)

                    for i in range(len(r_i)):
                        distances = self.distance_sim(radius, concentration, dopant = 'acceptor') 
                        tmp = np.ones(len(distances)) 
                        r_tmp = np.sum( np.power((tmp / distances),s))
                        r_i[i] = r_tmp


                    helper_funcs.cache_writer(r_i, process = process, radius = radius, concentration = concentration, iterations = iterations, interaction_type = interaction_type)
                case _ :
    
                    r_i = cache_data        
  
            return r_i    
            
         #TODO add exchange interation and cooperative process as an example
        

        def distplot_summary(self, radius: float, concentration: float, dopant: str = 'acceptor', filter: Optional[List[str]] = None) -> Union[None, Exception]:
            #TODO clean up plotting & formatting to produce thesis quality pictures & add saving option.
            #TODO port plotting to plotly
            """
            Generates a 3D scatter plot of the structure, with the central ion and its neighbors within a given radius.

            Parameters:
            radius (float/int): The radius within which to plot neighbors.
            concentration (float): The concentration of the dopant.
            dopant (str, optional): The type of dopant. Defaults to 'acceptor'.
            filter (list, optional): A list of species to plot. If not provided, all species are plotted.

            Returns:
            None. The function directly plots the 3D structure using matplotlib.
            """
            concentration = concentration / 100
            coords = self.structure.nearest_neighbours_coords(radius)
            filtered_coords = coords.loc[coords['species'].isin([self.structure.centre_ion_species])]
         
            coords = coords.drop(coords.index[coords['species'] == 'Y'])
           
            for i in filtered_coords.index:
        
                if np.random.rand() < concentration:
                    filtered_coords.loc[i, 'species'] = dopant
           

            frames = [coords, filtered_coords]

            result = pd.concat(frames)
            UniqueNames = result.species.unique()
            DataFrameDict = {elem : pd.DataFrame() for elem in UniqueNames}
            for key in DataFrameDict.keys():
                DataFrameDict[key] = result[:][result.species == key]
            
            fig = plt.figure()
            ax = fig.add_subplot(projection='3d') 
            ax.scatter(self.structure.origin[0] ,self.structure.origin[1] ,self.structure.origin[2], label=f'central {self.structure.centre_ion_species} ion')
            ax.set_xlabel('X (Angstrom)')
            ax.set_ylabel('Y (Angstrom)')
            ax.set_zlabel('Z (Angstrom)')
            if filter == None:
                for i in range(len(UniqueNames)):
                    temp = DataFrameDict[UniqueNames[i]]
                    ax.scatter(temp.x, temp.y, temp.z, label=UniqueNames[i])
                ax.legend()  
                self.fig = plt.gcf()  
                plt.show(block=False)       
            else:
                try:
                    for i in range(len(filter)):
                        temp = DataFrameDict[filter[i]] 
                        ax.scatter(temp.x, temp.y, temp.z, label=filter[i])   
                    ax.legend()  
                    self.fig = plt.gcf()  
                    plt.show(block=False)   
                except:
                    print('Failed to plot. Filter must be in type "list of strings"')
                    pass
      

if __name__ == "__main__":
    # cif file from https://materialsproject.org

    # Get the absolute path of the ciffiles directory
    cif_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cif_files'))
    cif_file = os.path.join(cif_dir, 'KY3F10_mp-2943_conventional_standard.cif')
    KY3F10 = Structure(cif_file= cif_file)
    KY3F10.centre_ion('Y')
    filtered_ions = ['F','K']
    KY3F10.structure_plot(5, filter = filtered_ions)   

    #rslt_df = coords_xyz.loc[coords_xyz['species'].isin(options)].reset_index(drop=True)
    #print(rslt_df)

    crystal_interaction = Interaction(KY3F10)

    #coords = crystal_interaction.distance_sim(radius=10, concentration = 15, dopant='Sm')
    #print(coords)
    #print(crystal_interaction.filtered_coords)
    interaction_components = crystal_interaction.sim_single_cross(radius=10, concentration = 5, iterations=50000, interaction_type= 'QQ')
    #print(interaction_components)
    #Interaction(KY3F10).distplot_summary(radius=20.0, concentration = 50.0 , dopant = 'Sm' , filter = ['Y','Sm'])
    #helper_funcs.cache_reader(process = 'singlecross', radius = 10 , concentration = 2.5 , iterations = 50000 , interaction_type = 'QQ')