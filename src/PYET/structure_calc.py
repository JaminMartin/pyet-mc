import numpy as np
import numpy.linalg as LA
from pymatgen.io.cif import CifParser
import matplotlib.pyplot as plt
import pandas as pd
from . import helper_funcs
import os
#add documentation
class Structure:
    '''
    A class for handling the structural info of a host crystal. A central ion, e.g. a Ytrrium ion must be specified for the associated methods to work. Once this ion has been specified the nearest neigbour ions can be calculated. This can either return cartesian or spherical polar coordinates for further calculations or plotting. There is also a simple function for printing off this information for a quick analyis. Lastly this class provides plotting functionality directly for visualisation purposes. 
    '''
    def __init__(self,cif_file):
        '''
        cif_file: a .cif file containing the structural information of the host material
        '''
        try:
            self.cif = CifParser(cif_file)
            self.struct = self.cif.get_structures()[0]
        except:
            print('Invalid or no CIF file provided')
          
    def centre_ion(self,ion):
        """
        Return the index of an ion ion of a given species choice

        ion: type string, e.g. "Y" 
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
        
    def nearest_neighbours_info(self, radius): 
        """
        Return the radial distance and species of the neighbors within radius r.
        radius: float/int value e.g 3.6.
        """ 
        self.nn = self.struct.get_neighbors(self.site, radius)
        s = ""
        heading = f"Nearest neighbours within radius {radius} Angstroms of a {self.centre_ion_species} ion:\n"
        s += (heading)
        for n in self.nn:
            s += "Species = %s, r = %f Angstrom\n" % (n[0].species.chemical_system, self.site.distance(n[0]))
        s += "\n"
        print(s)

    def nearest_neighbours_coords(self, radius): 
        """
        Return the distances and species of the next nearest neighbors within radius r in cartesian coordinates as a pandas dataframe.
        radius: float/int value e.g 3.6.
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
    
    def nearest_neighbours_spherical_coords(self,radius): 
        """
        Return the distances and species of the next nearest neighbors within radius r in spherical polar coordinates as a pandas dataframe.
        radius: float/int value e.g 3.6.
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
    
    def structure_plot(self, radius, filter = None):
        '''
        Renders a 3D plot of a given radius around a specified central ion. A filter can provided as a list of strings 
        radius: float/int value e.g 3.6.
        filter: list of strings e.g ["Y", "F"]
        '''
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
        if filter == None:
            for i in range(len(UniqueNames)):
                temp = DataFrameDict[UniqueNames[i]]
                ax.scatter(temp.x, temp.y, temp.z, label=UniqueNames[i])
            ax.legend()    
            plt.show()       
        else:
            try:
                for i in range(len(filter)):
                    temp = DataFrameDict[filter[i]] 
                    ax.scatter(temp.x, temp.y, temp.z, label=filter[i])   
                ax.legend()    
                plt.show()   
            except:
                  print('Failed to plot. Filter must be in type "list of strings"')
                  pass    

   
class Interaction:
        def __init__(self, Structure):
            try:
                self.structure = Structure
                print(f' Central ion is {self.structure.centre_ion_species}')
            except:
                print('Either structure or central ion is not specified')  
       

        
        def distance_sim(self,radius, concentration, dopant = 'acceptor'): 
            concentration = concentration / 100
            # returns the coordinates of the 
            coords = self.structure.nearest_neighbours_spherical_coords(radius)
            self.filtered_coords = coords.loc[coords['species'].isin([self.structure.centre_ion_species])].reset_index(drop=True)
            
       
            for i in self.filtered_coords.index:
                if np.random.rand() < concentration:
                    self.filtered_coords.loc[i, 'species'] = dopant
            
            distances = self.filtered_coords.loc[self.filtered_coords['species'].isin([dopant])].reset_index(drop=True)
            distances = distances['r'].to_numpy()
            return distances
        
        def sim_single_cross(self, radius, concentration, iter, interaction_type = None):
            '''
            
            '''
            process = 'singlecross'
            cache_data = helper_funcs.cache_reader(process = process, radius = radius, concentration = concentration, iter = iter, interaction_type = interaction_type)
            match cache_data: 
                case None:
                    print('File not found in cache, running simulation')
                    if interaction_type == 'DD':
                        s = 6
                    elif interaction_type == 'DQ': 
                        s = 8   
                    elif interaction_type == 'QQ':
                        s = 10
                    else:
                        'Please specify interaction type'   
                    r_i = np.zeros(iter)
                    for i in range(len(r_i)):
                        distances = self.distance_sim(radius, concentration, dopant = 'acceptor') 
                        tmp = np.ones(len(distances))
                        r_tmp = np.sum( np.power((tmp / distances),s))
                        r_i[i] = r_tmp


                    helper_funcs.cache_writer(r_i, process = process, radius = radius, concentration = concentration, iter = iter, interaction_type = interaction_type)
                case _ :
    
                    r_i = cache_data        
  
            return r_i    
            
         #TODO add exchange interation and cooperative process as an example
        

        def distplot_summary(self, radius, concentration, dopant = 'acceptor', filter = None):
            #TODO clean up plotting & formatting to produce thesis quality pictures & add saving option.
            #TODO port plotting to plotly
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
                plt.show()       
            else:
                try:
                    for i in range(len(filter)):
                        temp = DataFrameDict[filter[i]] 
                        ax.scatter(temp.x, temp.y, temp.z, label=filter[i])   
                    ax.legend()    
                    plt.show()   
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
    KY3F10.nearest_neighbours_info(3.2)
    coords_xyz = KY3F10.nearest_neighbours_coords(3.2)
    t1 = coords_xyz.species.unique() == 'F' 
    assert t1.all() == True , 'Only F ions should be present for this test.'
    filtered_ions = ['F']
    KY3F10.structure_plot(5, filter = filtered_ions)   

    #rslt_df = coords_xyz.loc[coords_xyz['species'].isin(options)].reset_index(drop=True)
    #print(rslt_df)

    #inter = Interaction(KY3F10)
    #inter.distance_sim(radius=10, concentration = 5, dopant='Sm')
    #print(inter.filtered_coords)
    #r = Interaction(KY3F10).sim_single_cross(radius=10, concentration = 5, interaction_type='QQ', iter=50000)
    #print(r)
    #Interaction(KY3F10).distplot_summary(radius=20, concentration = 5, dopant = 'Sm' , filter = ['Y','Sm'])
  