import numpy as np
import numpy.linalg as LA
from pymatgen.io.cif import CifParser

def centre_ion(struct,ion):
    structure_sites = struct.sites
    for i in range(len(structure_sites)):
        temp = structure_sites[i]
        if temp.species_string == ion:
            ion_index = i
            break
        
        else:
            pass    
    
    return ion_index
       
def nearest_neighbours(struct,central_ion, radius): 
    site = struct.sites[central_ion] #22 ky3f10 8 K2YF5 10 LiYF4 4 NaYF
    nn = struct.get_neighbors(site,radius)
    return nn, site

def nearest_neighbour_spherical_coords(struct, site, r): 
    """
    Return the spherical polar coordinates of the next nearest neighbors within radius r.
    """          
    NN = struct.get_neighbors(site, r)
    origin = site.coords
    
    spc = np.zeros([len(NN), 3])
    for i,N in enumerate(NN):
        xyz = N[0].coords-origin
        spc[i, 0] = LA.norm(xyz)
        spc[i, 1] = np.arccos(xyz[2]/spc[i,0])
        spc[i, 2] = np.arctan2(xyz[1],xyz[0])

    return spc

# cif file from https://materialsproject.org/materials/mp-19426/
cif_file = 'src/cif_files/KY3F10_mp-2943_conventional_standard.cif'
cif = CifParser(cif_file)
struct = cif.get_structures()[0]


   
donor_ion = centre_ion(struct=struct, ion = 'Y')
near_ions, site = nearest_neighbours(struct=struct, central_ion= donor_ion, radius = 3.2)
s = ""
heading = "Nearest neighbors\n"
s += (heading)
for n in near_ions:
    s += "Species = %s, r = %f Angstrom\n" % (n[0].species.chemical_system, site.distance(n[0]))
s += "\n"
print(s)