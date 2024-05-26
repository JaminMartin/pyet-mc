from pyet.structure import Structure, Interaction
from pyet.fitting import Optimiser, general_energy_transfer
from pyet.pyet_utils import Trace, cache_reader, cache_list, cache_clear
from pyet.plotting import Plot
import numpy as np 


if __name__ == "__main__":
    KY3F10 = Structure(cif_file= 'KY3F10.cif')

    KY3F10.centre_ion('Y3+')

    KY3F10.nearest_neighbours_info(3.2)
    fig1 = KY3F10.structure_plot(radius = 5)  
    fig1.show() 

    filtered_ions = ['F-', 'K+'] #again, note we must specify the charge!

    fig2 = KY3F10.structure_plot(radius = 5, filter = filtered_ions)  
    fig2.show() 

    crystal_interaction = Interaction(KY3F10)
    fig3 = crystal_interaction.doped_structure_plot(radius=7.0, concentration = 15.0 , dopant = 'Sm3+' , filter = ['Y3+','Sm3+'])
    fig3.show()

    interaction_components2pt5pct = crystal_interaction.sim_single_cross(radius=10, concentration = 2.5, interaction_type='DQ', iterations=1000)
    interaction_components5pct = crystal_interaction.sim_single_cross(radius=10, concentration = 5.0, interaction_type='DQ', iterations=1000)

    #specify additional constants (the time based constants are in ms^-1)
    const_dict1  = {'amplitude': 1 , 'energy_transfer': 500, 'radiative_decay' : 0.144, 'offset':0}
    const_dict2  = {'amplitude': 1 , 'energy_transfer': 500, 'radiative_decay' : 0.144, 'offset': 0}

    
    # generate some random data
    time = np.arange(0,21,0.02) #1050 data points 0 to 21ms
    #Generate some random data based on our provided constants and time basis
    data_2pt5pct = general_energy_transfer(time, interaction_components2pt5pct, const_dict1)
    data_5pct = general_energy_transfer(time, interaction_components5pct, const_dict2)
    #Add some noise to make it more realistic
    rng = np.random.default_rng()
    noise = 0.01 * rng.normal(size=time.size)
    data_2pt5pct = data_2pt5pct + noise
    data_5pct = data_5pct + noise
    
    #Plotting
    fig4 = Plot()
    fig4.transient(time, data_2pt5pct)
    fig4.transient(time, data_5pct)
    fig4.show()


    params2pt5pct = ['amp1', 'cr', 'rad', 'offset1']
    params5pct = ['amp2', 'cr', 'rad', 'offset2']

    trace2pt5pct = Trace(data_2pt5pct, time,  '2.5%', interaction_components2pt5pct)
    trace5pct = Trace(data_5pct, time, '5%', interaction_components5pct)

    opti = Optimiser([trace2pt5pct,trace5pct],[params2pt5pct,params5pct], model = 'rs')

    guess = {'amp1': 1, 'amp2': 1, 'cr': 100,'rad' : 0.500, 'offset1': 0 , 'offset2': 0}

    res = opti.fit(guess, method = 'Nelder-Mead', tol = 1e-13)



    fig5 = Plot()
    fig5.transient(trace2pt5pct)
    fig5.transient(trace5pct)
    #generate the data to show the fitted results 
    rdict = res.x #the dictionary within the result of the optimiser
    print(f'resulting fitted params:{res.x}')
    fit1 = general_energy_transfer(time, interaction_components2pt5pct, {'a': rdict['amp1'], 'b': rdict['cr'], 'c': rdict['rad'],'d': rdict['offset1']})
    fit2 = general_energy_transfer(time, interaction_components5pct, {'a': rdict['amp2'], 'b': rdict['cr'], 'c': rdict['rad'], 'd': rdict['offset2']})
    fig5.transient(time,fit1, fit=True, name = 'fit 2.5%')
    fig5.transient(time,fit2, fit = True, name = 'fit 5%')
    fig5.show()