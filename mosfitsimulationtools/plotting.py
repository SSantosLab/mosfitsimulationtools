# MOSFiT Simulation Tools
# plotting.py
# January 2019
# Kamile Lukosiute Thesis Code
# python2

# MOSFiT  (https://github.com/SSantosLab/MOSFiT) REQUIRED
# Built to work with the kasen_model model in MOSFIT (found in the SSantosLab 
# github)

# Plotting Tools for Mosfit Simulation Tools

import corner
import matplotlib.pyplot as plt
import json 
plt.switch_backend('agg')
import numpy as np
import seaborn as sns

class Plotting(object):

    def __init__(self):
        # Does every class need a init? I'm not sure so here it is, just in case
        pass
    
    def single_corner(self, analyze_single, name='corner.png', save=False, theta=True):
        '''
        Makes a smoll corner plot for the simulation
        
        analyze_single: a Single object from analyze.py 
        '''
        if theta:
           plt.rcParams["font.family"] = "serif"
           plt.rcParams.update({'font.size': 12})
           cfig = plt.figure(figsize=(8,10))
            
            
           sim_results = np.array(analyze_single.get_param_vals())*180/np.pi
           
           cfig = corner.corner(sim_results, quantiles=[.16, .50, .84], 
                         show_titles=True, labels=[r'$\theta_{meas}$'])
           cfig.axes[0].axvline(analyze_single.get_true_val(), color='red')
           cfig.suptitle(r'$\theta_{true}$ = ' +"{:.0f}".format(analyze_single.get_true_val()*180./np.pi), fontsize=16)
           plt.tight_layout(pad=1.7)
	   if save:
	       plt.savefig(name, dpi=300)

           return cfig
        else:
            return 0 
        
       
    def single_comparison(self,analyze_single, name='comparison.png', save=False):
        '''
        Make a comparison plot of the input data and the walkers on a 
        magnitude vs. MJD plot
        
        analyze_single: a Single object from analyze.py
        '''
     
        sns.reset_orig()
        plt.rcParams["font.family"] = "serif"
        plt.rcParams.update({'font.size': 14})

        fig = plt.figure(figsize=(12,8))
        plt.gca().invert_yaxis()
        plt.gca().set_xlim(0,4)
        #plt.gca().set_ylim(bottom=25, top=19)
        plt.gca().set_xlabel('MJD')
        plt.gca().set_ylabel('Apparent Magnitude')

        real_data = analyze_single.get_data()
        instruments = [] # should only ever be one instrument 
        bands = []
        
        for i in real_data:
            if i[u'band'] not in bands:
                bands.append(i[u'band'])
            if i[u'instrument'] not in instruments:
                instruments.append(i[u'instrument'])
            
        fake_data = analyze_single.get_determined_data()
        num_realizations = analyze_single.get_num_realizations()
        
        
        for band in bands: 
            # Plotting Simulated Sata
            for i in range(1, num_realizations+1):
                mag = []
                time = []
                for point in fake_data:
                    if int(point[u'realization']) == i and point[u'band'] == band:
                        mag.append(float(point[u'magnitude']))
                        time.append(float(point[u'time']))
                plt.plot(time, mag, '-', color=self.bandcolor(band))
                
            # Plotting real data
            mag = []
            time = []
            error = []
            for point in real_data:
                if point[u'band'] == band:
                    mag.append(float(point[u'magnitude']))
                    time.append(float(point[u'time']))
                    error.append(float(point[u'e_magnitude']))
                    
            plt.errorbar(time, mag, fmt='o' ,yerr=error, 
                         label=str(instruments[0]) + ' ' + str(band), 
                         markerfacecolor=self.bandcolor(band), markeredgecolor='k', ecolor='k')
            
        true, q_50, q_m, q_p = analyze_single.get_plotting_vals()*180/np.pi


        fmt = "{0:.2f}".format
        title = r"${{{0}}}_{{-{1}}}^{{+{2}}}$"
        title = title.format(fmt(q_50), fmt(q_m), fmt(q_p))
        plt.title(r'$\theta_{true}$ = ' +  	"{:.0f}".format(true) + r', $\theta_{meas}$ = ' + title)
        
        plt.legend()
        if save:
            plt.savefig(name, dpi=300)
        

    def money_plot(self, analyze_set, name='money.png', theta=True, save=False, truevtrue=True):
        '''
        Given a set of analyze.py objects, makes the money plot, ie the parameters
        determined versus set
        
        analyze_set: a Set object from analyze.py that contains a set of
        simulations
        theta=True: by default, I make the theta-centered plot because my thesis
        is all about that sweet sweet angle
        '''
        
        
        true, q50s, qms, qps = analyze_set.get_plotting_vals()*180/np.pi
        plt.errorbar(true, q50s, yerr=[qms, qps], fmt='ko')
        if truevtrue:
            plt.plot(true, true, '-', color='r')
        
        if theta:
            plt.xlabel(r'$\theta_{true}$')
            plt.ylabel(r'$\theta_{meas}$')

        if save:
            plt.savefig(name, dpi=300)
            
        

    def bandcolor(self,band):
        '''
        Generated with jet cmap with:
        for i in range(1,7):
            color = cm.jet(i/6.)
        '''
        colors = {u'u': (0.0, 0.0, 0.5647058823529412, 1.0),
                  u'g': (0.11335784313725483, 0.0, 1.0, 1.0),
                  u'r': (0.5545343137254901, 0.014901960784313717, 0.9850980392156864, 1.0),
                  u'i': (1.0, 0.30509803921568623, 0.6949019607843139, 1.0),
                  u'z': (1.0, 0.5874509803921569, 0.4125490196078432, 1.0),
                  u'Y':(1.0, 0.8776470588235293, 0.12235294117647078, 1.0)}
        return colors[band]
    
    
    def single_raw(self, 
                   data_path='data.json', 
                   name='input.png', 
                   save =False, 
                   title=' ',
                   connect = False,
                   xlim_min = 0,
                   xlim_max = 3.5,
                  ylim_t = 17,
                  ylim_b = 25):
        '''
        Plots the data from a single, already existing data set
        '''

        # Import data
        with open(data_path, 'r') as f:
            data = json.loads(f.read())
            if 'name' not in data:
                data = data[list(data.keys())[0]]

        sns.reset_orig()
        plt.rcParams["font.family"] = "serif"
        plt.rcParams.update({'font.size': 14})

        fig = plt.figure(figsize=(12,8))
        plt.gca().invert_yaxis()
        plt.gca().set_xlim(xlim_min, xlim_max)
        plt.gca().set_ylim(bottom=ylim_b, top=ylim_t)
        plt.gca().set_xlabel('MJD')
        plt.gca().set_ylabel('Apparent Magnitude')

        real_data = data['photometry']
        instruments = [] # should only ever be one instrument 
        bands = []

        for i in real_data:
            if i[u'band'] not in bands:
                bands.append(i[u'band'])
            if i[u'instrument'] not in instruments:
                instruments.append(i[u'instrument'])

        for band in bands: 
            # Plotting real data
            mag = []
            time = []
            error = []
            for point in real_data:
                if point[u'band'] == band:
                    mag.append(float(point[u'magnitude']))
                    time.append(float(point[u'time']))
                    error.append(float(point[u'e_magnitude']))

            plt.errorbar(time, mag, fmt='o-' ,yerr=error, 
                         label=str(instruments[0]) + ' ' + str(band), 
                         markerfacecolor=self.bandcolor(band), markeredgecolor='k', ecolor='k', color=self.bandcolor(band))

        plt.legend()
        plt.title(title)
        if save:
            plt.savefig(name, dpi=300)
            
            
    def single_raw_comparison(self, data_paths=['data.json'], labels=[" "], name='input.png', save =False, band=u'g'):
        '''
        Plots the data from a single, already existing data set
        '''
        sns.reset_orig()
        plt.rcParams["font.family"] = "serif"
        plt.rcParams.update({'font.size': 14})

        fig = plt.figure(figsize=(12,8))
        plt.gca().invert_yaxis()
        #plt.gca().set_xlim(55700,55820)
        #plt.gca().set_ylim(bottom=25, top=19)
        plt.gca().set_xlabel('MJD')
        plt.gca().set_ylabel('Apparent Magnitude')

        colors = ['xkcd:darkblue',
                  'xkcd:blue',
                  'xkcd:aqua',
                  'xkcd:lightblue',
                  'xkcd:lime',
                  'xkcd:green',
                  'xkcd:darkgreen',
                  'xkcd:goldenrod',
                  'xkcd:orange',
                  'xkcd:maroon',
                  'xkcd:salmon',
                  'xkcd:red',
                  'xkcd:magenta',
                  'xkcd:plum',
                  'xkcd:lavender',
                  'xkcd:purple'
               
                   ]
        '''
        (0.0, 0.0, 0.5647058823529412, 1.0), 
                  (0.11335784313725483, 0.0, 1.0, 1.0), 
                  (0.5545343137254901, 0.014901960784313717, 0.9850980392156864, 1.0), 
                  (1.0, 0.30509803921568623, 0.6949019607843139, 1.0),
                  (1.0, 0.5874509803921569, 0.4125490196078432, 1.0),
                  (1.0, 0.8776470588235293, 0.12235294117647078, 1.0)
        '''
        for data_path, label, color in zip(data_paths, labels, colors):

            # Import data
            with open(data_path, 'r') as f:
                data = json.loads(f.read())
                if 'name' not in data:
                    data = data[list(data.keys())[0]]


            real_data = data['photometry']
            instruments = [] # should only ever be one instrument 
            bands = []

            for i in real_data:
                if i[u'band'] not in bands:
                    bands.append(i[u'band'])
                if i[u'instrument'] not in instruments:
                    instruments.append(i[u'instrument'])

            for band_to_use in bands: 
                if band_to_use == band:
                    # Plotting real data
                    mag = []
                    time = []
                    error = []
                    for point in real_data:
                        if point[u'band'] == band:
                            mag.append(float(point[u'magnitude']))
                            time.append(float(point[u'time']))
                            error.append(float(point[u'e_magnitude']))

                    plt.errorbar(time, mag, fmt='-o' ,yerr=error, 
                                 label=str(instruments[0]) + ' ' + str(band) + ' ' + label,
                                 color=color)

        plt.legend(bbox_to_anchor=(1.05, 1))
        if save:
            plt.savefig(name, dpi=300)


