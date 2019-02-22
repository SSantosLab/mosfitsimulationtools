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
True: [0.   1.57] 
Mean: [0.69155941 1.31032365]
Plus (q84): [0.38943835 0.13992739]
Minus (q16): [0.32618351 0.17289212]  
'''
## TEST PLOTTING
# -----------------------------------------------------------------------------
plotting = mst.plotting.Plotting()
plotting.money_plot(results, truevtrue=True, save=True)

single_data = mst.analyze.Single(freeparamname='theta', 
                             trueval=1.57, 
                             datapath='./test/theta90/run/products/walkers.json')
plotting.single_corner(single_data, save=True)
plotting.single_comparison(single_data, save=True)
