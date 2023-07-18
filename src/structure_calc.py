import numpy as np
import numpy.linalg as LA
from pymatgen.io.cif import CifParser
import matplotlib.pyplot as plt
import pandas as pd


class Structure:

    def __init__(self,cif_file):
        try:
            self.cif = CifParser(cif_file)
            self.struct = self.cif.get_structures()[0]
        except:
            print('Invalid or no CIF file provided')
          
    def centre_ion(self,ion):
        """
        Return the index of an ion ion of a given species choice
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
        """ 
        self.nn = self.struct.get_neighbors(self.site, radius)
        s = ""
        heading = f"Nearest neighbors within radius {radius} Angstroms of a {self.centre_ion_species} ion:\n"
        s += (heading)
        for n in self.nn:
            s += "Species = %s, r = %f Angstrom\n" % (n[0].species.chemical_system, self.site.distance(n[0]))
        s += "\n"
        print(s)

    def nearest_neighbours_coords(self, radius): 
        """
        Return the distances and species of the next nearest neighbors within radius r in cartesian coordinates as a pandas dataframe.
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
        Renders a 3D plot of a given radius around a specified central ion
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
            coords = self.structure.nearest_neighbours_spherical_coords(radius)
            self.filtered_coords = coords.loc[coords['species'].isin([self.structure.centre_ion_species])].reset_index(drop=True)
            
       
            for i in self.filtered_coords.index:
                if np.random.rand() < concentration:
                    self.filtered_coords.loc[i, 'species'] = dopant
            
            distances = self.filtered_coords.loc[self.filtered_coords['species'].isin([dopant])].reset_index(drop=True)
            distances = distances['r'].to_numpy()
            return distances
        
        def sim_single_cross(self, radius, concentration, iter, interaction_type = None):
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

            return r_i    
            


        def distplot_summary(self, radius, concentration, dopant = 'acceptor', filter = None):
            concentration = concentration / 100
            coords = self.structure.nearest_neighbours_coords(radius)
            filtered_coords = coords.loc[coords['species'].isin([self.structure.centre_ion_species])]
         
            coords = coords.drop(coords.index[coords['species'] == 'Y'])
            print(filter)
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
      



# cif file from https://materialsproject.org
cif_file = 'src/cif_files/KY3F10_mp-2943_conventional_standard.cif'
KY3F10 = Structure(cif_file= cif_file)
KY3F10.centre_ion('Y')
#KY3F10.nearest_neighbours_info(radius = 3.2)
#coords_spc = KY3F10.nearest_neighbours_spherical_coords(3.2)
#coords_xyz = KY3F10.nearest_neighbours_coords(5)
#KY3F10.structure_plot(radius = 5)


#options = ['Y']
#KY3F10.structure_plot(5, filter=options)   

#rslt_df = coords_xyz.loc[coords_xyz['species'].isin(options)].reset_index(drop=True)
#print(rslt_df)

inter = Interaction(KY3F10)
inter.distance_sim(radius=10, concentration = 5, dopant='Sm')
print(inter.filtered_coords)
r = Interaction(KY3F10).sim_single_cross(radius=10, concentration = 5, interaction_type='DD', iter=500)
print(r)
#Interaction(KY3F10).distplot_summary(radius=20, concentration = 5, dopant = 'Sm' , filter = ['Y','Sm'])
#Quadpole_Quadpole = Interaction(KY3F10).sim(distances= Distances,interaction_type='Quadrapole-Quadrapole')