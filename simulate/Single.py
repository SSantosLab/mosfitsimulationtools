# MOSFiT Simulation Tools
# simulate.Single
# January 2019
# Kamile Lukosiute Thesis Code
# python2

# MOSFiT  (https://github.com/SSantosLab/MOSFiT) REQUIRED
# Built to work with the kasen_model model in MOSFIT (found in the SSantosLab 
# github)

import subprocess
import json
import os
import numpy as np

class Single(object):
    """
    Represents a single data set made with MOSFiT in generative mode. 
    
    Specify the parameters of the simulation, and this object will call MOSFiT 
    through subprocess and run the simulation, saving the output data file, 
    which can then be read in.
    """

    def __init__(self, name, model='kasen_model',
                 max_time = 3, 
                 instrument = 'DECam', 
                 telescope = 'CTIO',
                 bands = ['u', 'g', 'r', 'i', 'z', 'Y'],
                 S = 100, # Smoothness parameter, check MOSFiT docs
                 param_vals = [('Msph1', 0.04), ('vk1', 0.1), ('xlan1', 1e-2 ),
                               ('theta', 0.0), ('phi', 0.7), ('Msph0', 0.025),
                               ('vk0', 0.3), ('xlan0',1e-4)] ):
        ''' 
        Specify the terms of the simulation, built in defaults are for the
        kasen_model
        '''
    
        self.name = name
        self.model = model
        self.max_time = max_time
        self.instrument = instrument
        self.bands = bands
        self.S = S
        self.param_vals = param_vals
        self.telescope = telescope
        

    def generate(self):
        '''
        Creates a MOSFiT command, creates the directory from which MOSFiT will
        be called, calls MOSFiT.
        
        Returns the suprocess call code
        '''
        
        command = self.create_mosfit_gen_command()
        old_path = os.getcwd()
        
        self.path = old_path + '/' + self.name
        try:
            os.mkdir(self.path)
        except OSError:
            print("Making directory " + self.name + " failed.")
            
        os.chdir(self.path)
        call = subprocess.call(command, shell =True)
        os.chdir(old_path)
        
        return call
               
        
    def create_mosfit_gen_command(self):
        '''
        A helper for generate() that generates the command that calls MOSFiT in
        generative mode
        '''
        param_list = []
        for i in self.param_vals:
            param_list.append(str(i[0]))
            param_list.append(str(i[1]))
            
        param_str = " ".join(param_list)
        
        command = ('mosfit -m ' + self.model + ' --band-instruments ' + 
                   self.instrument + " --band-list " + " ".join(self.bands) +
                   ' --max-time ' + str(self.max_time) +" -F " + param_str + 
                   ' ' + " " + str(self.S) + " " + 
                   '--no-copy-at-launch -N 1 ' ) 
        
        return command
    
    
    def generate_input_file(self, N = 20, error = 0.02):
        '''
        Generates an input file for the evaluative run of MOSFiT
        '''
        self.sampleN = N
        self.sampleerr = error
        
        with open('./' + self.name +'/products/walkers.json', 'r') as f:
            data = json.loads(f.read())
            if 'name' not in data:
                data = data[list(data.keys())[0]]
        
        photo = data['photometry']

        # Remove dict entries we don't need
        for i in photo:
            del i[u'model']
            del i[u'realization']
            del i[u'source']
            i[u'e_magnitude'] = error
            i[u'source'] = '1'
            i[u'telescope'] = self.telescope
            i[u'system'] = 'AB'
        
        # Bands but unicode
        bands_unicode = [unicode(s) for s in self.bands]
        
        # Keep only the right bands
        photo_reduced = []
        for band in bands_unicode:
            p = [i for i in photo if i[u'band'] == band]
            photo_reduced.append(p)
            
        photo_reduced_2 = []

        for p in photo_reduced:
            # get evenly spaced N indices, approx. from 0 to len(p)
            # new_p contains that slice from p
            l = len(p)
            ind = [int(i*l/N) for i in range(0,N)]
            new_p = [p[i] for i in ind]
            photo_reduced_2.append(new_p)


        photo_reduced_3 = [obs for band_sublist in photo_reduced_2 for obs in band_sublist]
    
        self.mock_sample = {self.name: {'name': self.name,"sources":[{"name":"MOSFiT generated data", "alias":"1"}],
                    "alias":[{"value":"MOSFiT generated data","source":"1"}], 'photometry': photo_reduced_3}}

        self.dump_path = self.path + '/' + self.name + '.json'

        with open( self.dump_path, 'w') as outfile:
            json.dump(self.mock_sample, outfile, indent=4)

        # we want to make a directory here where MOSFiT will eventually be run
        # Because if you're making an input file... then you're also going
        # to be running the thing, most likely
        run = self.path + '/run'
        try:
            os.mkdir(run)
        except OSError:
            print("Making directory " + run + " failed.")
            
        return self.dump_path, run 
        
        
    def get_observation_data(self):
        '''
        Returns the dictionary that has the observations created with MOSFiT,
        if you're in the mood to get fancy and try to do some notebook analysis
        '''
        return self.mock_sample
    