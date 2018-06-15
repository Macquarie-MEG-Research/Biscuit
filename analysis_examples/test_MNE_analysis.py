#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 13:58:42 2018

@author: 44737483 (Robert Seymour)
"""
###############################################################################
## Import
import mne
import numpy as np
from mne.preprocessing import ICA
from mne.time_frequency import (tfr_multitaper)

## Specify Paths
data_path = '/Users/44737483/Documents/alien_data/RS_pilot/2630_RS_PI160_2017_08_04_B1.con'
mrk = '/Users/44737483/Documents/alien_data/RS_pilot/2630_RS_PI160_2017_08_04_ini.mrk'
hsp = '/Users/44737483/Documents/alien_data/RS_pilot/2630_RS_PI160_2017_08_04.hsp'
elp = '/Users/44737483/Documents/alien_data/RS_pilot/2630_RS_PI160_2017_08_04.elp'

## Load Raw
raw = mne.io.read_raw_kit(data_path, mrk=mrk, elp=elp, hsp=hsp,
                          stim=['177','178'],slope='+',stim_code='channel',
                               preload=True)

# Check layout is working
layout = mne.find_layout(raw.info,ch_type='meg')

###############################################################################
# Notch Filter (remove 50Hz line noise and harmonics)
picks = mne.pick_types(raw.info, meg='mag',eeg=False, eog=False,
                       stim=False, exclude='bads')

raw.notch_filter(np.arange(50, 251, 50), picks=picks)

# BP Filter between 0.1-150Hz
raw.filter(0.1,150,picks=picks)

# Resample to 200Hz to speed up computation
raw.resample(200, npad="auto")  # set sampling frequency to 200Hz

# Plot the PSD
raw.plot_psd(area_mode='range', tmax=1.0, average=False)     

###############################################################################
## ICA
method = 'fastica'

# Choose other parameters
n_components = 20  # if float, select n_components by explained variance of PCA
decim = 3  # we need sufficient statistics, not all time points -> saves time

# we will also set state of the random number generator - ICA is a
# non-deterministic algorithm, but we want to have the same decomposition
# and the same order of components each time this tutorial is run
random_state = 23

ica = ICA(n_components=n_components, method=method, random_state=random_state)
reject = dict(mag=5e-12, grad=4000e-13)

ica.fit(raw, picks=picks, decim=decim, reject=reject)

ica.plot_components()

###############################################################################
## Epoch
events = mne.find_events(raw,stim_channel='STI 014')
print('Number of events:', len(events))
print('Unique event codes:', np.unique(events[:, 2]))
event_id = {'Grating': 177, 'Clicktrain': 178}

epochs = mne.Epochs(raw, events, event_id, tmin=-2, tmax=2,
                    baseline=(None, 0), preload=True)

###############################################################################
## Select Epochs and Average
grating = epochs['Grating']
clicktrain = epochs['Clicktrain']

# Average the grating trials and plot
grating.average().plot()
grating.average().plot_topo()

# Plot how the ERF changes from 0.05-0.3s
times = np.arange(0.05, 0.3, 0.05)
grating.average().plot_topomap(times=times, ch_type='mag')

###############################################################################
## TFR
# Define frequencies 1-100 in 2Hz steps
freqs = np.arange(1.0, 100.0, 2.0)

n_cycles = freqs / 2.
time_bandwidth = 8.0  # Use multiple tapers (this will take a while)
power = tfr_multitaper(grating, freqs=freqs, n_cycles=n_cycles,picks=picks,
                       time_bandwidth=time_bandwidth, return_itc=False)

## Plot visual gamma :)

# Pick an occipital sensor for show
picks_occ = mne.pick_types(raw.info, meg='mag',eeg=False, eog=False,
                       stim=False, exclude='bads',selection=['MEG 140'])

power.plot(picks=picks_occ, baseline=(-1.5, 0.),fmin=40,tmin=-1.5,
           tmax=1.5, mode='logratio',title='RS Gamma Occipital Sensor (MEG140)')

# Plot a whole-sensor layout
power.plot_topo(baseline=(-1.5, 0),tmin=-1.5,tmax=1.5, mode='logratio')

# Show visual gamma (40-70Hz) from 0.3-1.5s
power.plot_topomap(baseline=(-1.5, 0), fmin=40,fmax=70,tmin=0.3,
                   tmax=1.5,mode='logratio')

# Show how visual gamma changes over time from 
times = np.arange(-1.5, 1.5, 0.2)

for t in times:
    power.plot_topomap(baseline=(-1.5, 0), fmin=40,fmax=70,tmin=t-0.1,tmax=t+0.1, 
                   ch_type='mag',mode='logratio',title=('%f s'%(t)))















