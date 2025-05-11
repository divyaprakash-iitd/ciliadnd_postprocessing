#!/usr/bin/env python3
import pandas as pd
import h5py
import numpy as np
import pickle
from generate_signatures import find_extreme_window
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences

# Initialize an empty list
allciliafeatures = []

# Read the base values
base_values = np.loadtxt('base_values.txt', delimiter=',')

ncilia = 6
with open('simdata_tip.pkl', 'rb') as f:
    simdata_tip = pickle.load(f)
    for icilia in range(ncilia):
        # print(icilia)
        nsim = len(simdata_tip)
        
        # List of features for each cilia
        maxdef = np.zeros((nsim,)) # 1: Maximum perturbation
        carea = np.zeros((nsim,))  # 2: Area under the curve
        swidth = np.zeros((nsim,)) # 3: Width of signal
        npeaks = np.zeros((nsim,)) # 4: Number of peaks
         
        
        # Specify the component 
        xidx, yidx = 0, 1
        compidx = xidx
        compmaskidx = (compidx % 2) + 2
        
        # compmaskidx = ymaskidx
        for isim in range(nsim):
            # Convert the mask to bool
            boolmask = simdata_tip[isim][:,icilia,compmaskidx].astype(bool)
            
            # Extract the signal
            x = simdata_tip[isim][boolmask,icilia,compidx]
            
            # Measure from the datum
            datum = base_values[icilia,compidx]
            x = np.abs(x-datum)
            
            peaks, _ = find_peaks(x)
            
            # if len(peaks) < 2:
            # print(f'NPeaks: {len(peaks)}, Sim No: {isim}, Cilia No: {icilia} ')
            
            # Feature-1: Distance of peak/valley from the datum
            maxdef[isim] = np.abs(x.min() - x.max())
            
            # Feature-2: Calculate area enclosed by the curve and the baseline/datum
            carea[isim] = np.trapezoid(x)
            
            # Feature-3: Width of signal
            swidth[isim] = len(x)
            
            # Feature-4: Number of peaks
            npeaks[isim] = len(peaks)
            
            if icilia == 0:            
                plt.plot(x)

        ciliafeatures = np.vstack((maxdef, carea, swidth, npeaks)) 

        allciliafeatures.append(ciliafeatures)
 
plt.show()

icilia, ifeature = 0, 0
plt.plot(allciliafeatures[icilia][ifeature],'-o')

plt.show()
