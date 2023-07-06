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
        
        
    def nearest_neighbours(self, radius): 
        """
        Return the distances and species of the next nearest neighbors within radius r.
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
        Return the distances and species of the next nearest neighbors within radius r.
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
        nearest_neigbours = pd.concat([coordinate_df,Species_info],axis=1)
        return nearest_neigbours   
    
    def nearest_neighbours_spherical_coords(self,radius): 
        """
        Return the spherical polar coordinates of the next nearest neighbors within radius r.
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

        Species_info = np.asarray(Species_info)
        return spc, Species_info
    
    def structure_plot(self, radius):
        coords_xyz = self.nearest_neighbours_coords(radius)
        UniqueNames = coords_xyz.species.unique()

        DataFrameDict = {elem : pd.DataFrame() for elem in UniqueNames}
        for key in DataFrameDict.keys():
            DataFrameDict[key] = coords_xyz[:][coords_xyz.species == key]
        
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d') 
        ax.scatter(self.origin[0],self.origin[1],self.origin[2])
        for i in range(len(UniqueNames)):
            temp = DataFrameDict[UniqueNames[i]]
            ax.scatter(temp.x,temp.y,temp.z)
        plt.show()       
   



# cif file from https://materialsproject.org
cif_file = 'src/cif_files/KY3F10_mp-2943_conventional_standard.cif'
KY3F10 = Structure(cif_file= cif_file)
KY3F10.centre_ion('Y')
KY3F10.nearest_neighbours(radius = 3.2)
coords, species = KY3F10.nearest_neighbours_spherical_coords(3.2)
print(coords)
print(species)
coords_xyz = KY3F10.nearest_neighbours_coords(5)
print(coords_xyz)
KY3F10.structure_plot(3.2)