# MOSFiT Simulation Tools
# analyze.Set
# January 2019
# Kamile Lukosiute Thesis Code
# python2

# MOSFiT  (https://github.com/SSantosLab/MOSFiT) REQUIRED
# Built to work with the kasen_model model in MOSFIT (found in the SSantosLab 
# github)

# After running the script outputted by simulate.py ('simulation_script'),
# we need a way to analyze all that output. This is the script that creates
# the data structures you'll need to make your pretty plots and do all
# sorts of analysis

import json
import numpy as np

class Set(object):
    '''
    Represents a set of single simulations output by MOSFiT after parameter
    determination
    '''
    def __init__(self, freeparamname, data_path_file):
        # the data path file contains a pairing of true_val : run location
        # can be gotten from simulate.Set.get_run_paths()
        self.free_param = freeparamname
        self.datapaths = {}        
        f = open(data_path_file, 'r')
        for line in f:
            val, path = line.split(' ')
            self.datapaths[float(val)] = path
        f.close()
    
        self.simulations = []
        for val in self.datapaths:
            walkers = self.datapaths[val].strip() + "/products/walkers.json" 
            simulation = Single(freeparamname = self.free_param, trueval = val,
                                datapath = walkers)
            
            self.simulations.append(simulation)
            
    def get_quantiles(self):
        q16s = []
        q50s = []
        q84s = []
        
        for i in self.simulations:
            q16, q50, q84 = i.get_quantitles()
            q16s.append(q16)
            q50s.append(q50)
            q84s.append(q84)

        return q16s, q50s, q84s

    def get_simulations(self):
        return self.simulations
            