# MOSFiT Simulation Tools
# test_analysis_mst.py
# January 2019
# Kamile Lukosiute Thesis Code
# python2

# MOSFiT  (https://github.com/SSantosLab/MOSFiT) REQUIRED
# Built to work with the kasen_model model in MOSFIT (found in the SSantosLab 
# github)

import analyze
import plotting

## Before running this, you must run test_creation_mst.py
# REPLACE THE LINE BELOW TO MATCH YOUR PATH
# -----------------------------------------------------------------------------
run_locs_file = "./test/run_paths"
# -----------------------------------------------------------------------------

results = analyze.Set('theta', run_locs_file)
quantiles = results.get_quantiles()
print(quantiles)

# Should yield something close to what is below
# But MCMC isn't determinative, so you know, it'll be something different
'''
([0.13016566496298526, 1.0758381633834104], 
[0.4805015081827334, 1.2351341039914703], 
[1.2722618301848712, 1.4341241286371136])
'''
## TEST PLOTTING
# -----------------------------------------------------------------------------
all_data_set = analyze.Set('theta', './test/run_paths')
plotting.money_plot(all_data_set, truevtrue=True, save=False)

single_data = analyze.Single(freeparamname='theta', 
                             trueval=0, 
                             datapath='./test/theta0/run/products/walkers.json')
plotting.single_corner(single_data)
plotting.single_comparison(single_data, './test/theta0/theta0.json')
