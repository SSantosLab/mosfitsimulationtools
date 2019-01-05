 
# MOSFiT Simulation Tools
# simulate.py
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
    
class Set(object):
    """
    Represents a set of Single objects with modifications that free certain
    parameters in order to run MOSFiT in determinative mode 
    """
    
    def __init__(self, name='new_set',
                 model='kasen_model',
                 max_time = 3, 
                 instrument = 'DECam', 
                 telescope = 'CTIO',
                 bands = ['u', 'g', 'r', 'i', 'z', 'Y'],
                 S = 100,
                 fixed_params = [('Msph1', 0.04), ('vk1', 0.1), ('xlan1', 1e-2 ),
                                ('phi', 0.7), ('Msph0', 0.025),
                               ('vk0', 0.3), ('xlan0',1e-4)],
                 free_params = [('theta', np.linspace(0,1.57,10))],
                 N_obs_per_band = 20,
                 mag_err = 0.002,
                 num_walkers = 100,
                 num_iterations = 500):
        
        self.name = name
        self.model = model
        self.max_time = max_time
        self.instrument = instrument
        self.bands = bands
        self.S = S
        self.telescope = telescope

        self.fixed_params = fixed_params
        self.free_params = free_params
        self.N = N_obs_per_band
        self.mag_err = mag_err
        self.num_walkers = num_walkers
        self.num_iterations = num_iterations
        
    
    def generate(self):
        '''
        Creates a set of Single objects, which are mock observations, with 
        varying parameters specified by initialization
        '''
        
        self.run_commands = []
        self.run_locs = {}

        old_path = os.getcwd()
        self.path = old_path + '/' + self.name
        try:
            os.mkdir(self.path)
        except OSError:
            print("Making directory " + self.name + " failed.")
        os.chdir(self.path)

        for free in self.free_params: # for each free parameter
        # Only allowed to vary one parameter at a time! 
            free_param_name = free[0]
            for val in free[1]: # for each value available
                if free_param_name == 'theta' or free_param_name == 'phi':
                    sim_name = free_param_name + '{:.0f}'.format(val*180/np.pi)
                else:
                    sim_name = free_param_name + str(val)
                print('Now generating... ' + sim_name)
                mock = Single(sim_name, param_vals = self.fixed_params + [(free_param_name, val)], 
                    model = self.model,
                    max_time = self.max_time, 
                    instrument = self.instrument,
                    telescope = self.telescope,
                    bands = self.bands,
                    S = self.S )
                mock.generate()
                input_file_loc, run_dir = mock.generate_input_file(N=self.N, error=self.mag_err)

                self.run_commands.append(self.generate_mosfit_run_command(walker_path=input_file_loc,
                    run_loc = run_dir, num_walkers=self.num_walkers))
                self.run_locs[val] = run_dir

        # create the run locs file
        f = open("run_paths", 'w')
        for i in self.run_locs:
            f.write(str(i) + ' ' + self.run_locs[i] + '\n')
        f.close()


        self.create_bash_scripts()
        os.chdir(old_path)
        
        return 0
    
    
    def get_all_run_commands(self):
        '''
        Returns the MOSFiT input commands of the simulation set
        '''
        return self.run_commands
    
    def generate_mosfit_run_command(self, walker_path=None,
        run_loc = None,
        num_walkers = 0):
        '''
        A helper function that creates the MOSFiT generative command for a 
        single simulation
        '''
        
        param_list = []
        for i in self.fixed_params:
            param_list.append(str(i[0]))
            param_list.append(str(i[1]))
            
        param_str = " ".join(param_list)

        if walker_path == None:
            walker_path = self.dump_path

        if num_walkers == 0:
            num_walkers = 2 * len(self.free_params)


        mosfit_command = ('mosfit -m ' + self.model + ' -e ' + walker_path + 
            ' --band-instruments ' +  self.instrument + " --band-list " + 
            " ".join(self.bands) + ' --max-time ' + str(self.max_time) + 
            " -F " + param_str + " " + 
             '--no-copy-at-launch -N ' + str(num_walkers) + ' -i ' +
             str(self.num_iterations) + ' --local-data-only')

        full_command = 'cd ' + run_loc + ' && ' + mosfit_command + ' && cd'

        return full_command
    
        
    def create_bash_scripts(self, num_per_screen = 5):
        '''
        A helper that creats the script that will create the screen sessions 
        and run MOSFiT in generative mode
        '''
        run_commands = self.get_all_run_commands()
        k = num_per_screen
        run_blocks = [run_commands[i:i+k] for i in range(0, len(run_commands), k)]
        # Write the inner scripts
        for i in range(0, len(run_blocks)):
            f = open("run_script_" + str(i), 'w')
            f.write("#!/usr/bin/env bash\n")
            for j in run_blocks[i]:
                f.write(str(j)+'\n')
            f.close()
        
        # Now write the simulation script
        f = open("simulation_script", 'w')
        f.write("#!/usr/bin/env bash\n")
        f.write("chmod +x run_script_*\n")
        for i in range(0, len(run_blocks)):
            f.write("screen -S " + str(i) + " -d -m ./run_script_" + str(i) + "\n")
        
        f.close()
        
    def get_run_paths(self):
        return self.run_locs
        
        