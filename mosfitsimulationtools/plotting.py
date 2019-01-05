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
           sim_results = analyze_single.get_param_vals()
           cfig = corner.corner(sim_results, quantiles=[.16, .50, .84], 
                         show_titles=True, labels=[r'$\theta$'])
           cfig.axes[0].axvline(analyze_single.get_true_val(), color='red')
        else:
            pass
       
        return cfig

    def single_comparison(self,analyze_single, input_data_path, name='comparison.png', save=False):
        '''
        Make a comparison plot of the input data and the walkers on a 
        magnitude vs. MJD plot
        
        analyze_single: a Single object from analyze.py
        input_data_path: path to the input data file that was used to run the
        simulation
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
                         color=self.bandcolor(band))
            
            
            
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
        true_vals = []
        for sim in analyze_set.get_simulations():
            true_vals.append(sim.get_true_val())
            
            
        q16s, q50s, q84s = analyze_set.get_quantiles()
        q50a = np.array(q50s) 
        q16a = np.abs(np.array(q16s) - q50a)
        q84a = np.array(q84s) -q50a
        
        # convert everything to degrees
        true = np.array(true_vals)*180/np.pi
        q50d = q50a*180/np.pi
        q16d = q16a*180/np.pi
        q84d = q84a*180/np.pi
        
        plt.errorbar(true, q50d, yerr=[q16d, q84d], fmt='ko')
        
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