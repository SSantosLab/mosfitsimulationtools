# MOSFiT Simulation Tools
# test_analysis_mst.py
# January 2019
# Kamile Lukosiute Thesis Code
# python2

# MOSFiT  (https://github.com/SSantosLab/MOSFiT) REQUIRED
# Built to work with the kasen_model model in MOSFIT (found in the SSantosLab 
# github)

import sys
sys.path.append('../')

import mosfitsimulationtools as mst

## Before running this, you must run test_creation_mst.py
# REPLACE THE LINE BELOW TO MATCH YOUR PATH
# -----------------------------------------------------------------------------
run_locs_file = "./test/run_paths"
# -----------------------------------------------------------------------------

results = mst.analyze.Set('theta', run_locs_file)
true, q50s, qms, qps = results.get_plotting_vals()
print('True: {0} , Mean: {1}, Plus (q84): {2}, Minus (q16): {3}'.format(true, q50s, qms, qps))

# Should yield something close to what is below
# But MCMC isn't determinative, so you know, it'll be something different
'''
True: [0.   1.57] , 
Mean: [0.31598286 1.19908933], 
Plus (q84): [0.15059294 0.41182856], 
Minus (q16): [0.35850292 0.28549421]
'''
## TEST PLOTTING
# -----------------------------------------------------------------------------
plotting = mst.plotting.Plotting()
plotting.money_plot(results, truevtrue=True, save=False)

single_data = mst.analyze.Single(freeparamname='theta', 
                             trueval=0, 
                             datapath='./test/theta0/run/products/walkers.json')
plotting.single_corner(single_data)
plotting.single_comparison(single_data, './test/theta0/theta0.json')
