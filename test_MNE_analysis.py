#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 13:58:42 2018

@author: 44737483 (Robert Seymour)
"""

## Import
import mne
import numpy as np
from mne.baseline import rescale
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

# Notch Filter (remove 50Hz line noise)
picks = mne.pick_types(raw.info, meg='mag',eeg=False, eog=False,
                       stim=False, exclude='bads')

raw.notch_filter(np.arange(50, 251, 50), picks=picks)

raw.filter(1,150,picks=picks)
# Resample to 200Hz
raw.resample(200, npad="auto")  # set sampling frequency to 100Hz

# Plot the PSD
raw.plot_psd(area_mode='range', tmax=1.0, average=False)     

## Epoch
events = mne.find_events(raw,stim_channel='STI 014')
print('Number of events:', len(events))
print('Unique event codes:', np.unique(events[:, 2]))
event_id = {'Grating': 177, 'Clicktrain': 178}

epochs = mne.Epochs(raw, events, event_id, tmin=-2, tmax=2,
                    baseline=(None, 0), preload=True)

## Select Epochs and Average
grating = epochs['Grating']
clicktrain = epochs['Clicktrain']

grating.average().plot_topomap(ch_type='mag')

## TFR
# Define frequencies 1-100 in 1Hz steps
freqs = np.arange(1.0, 100.0, 1.0)

# Pick an occipital sensor for show
picks_occ = mne.pick_types(raw.info, meg='mag',eeg=False, eog=False,
                       stim=False, exclude='bads',selection=['MEG 140'])

n_cycles = freqs / 2.
time_bandwidth = 8.0  # Use multiple tapers
power = tfr_multitaper(grating, freqs=freqs, n_cycles=n_cycles,picks=picks_occ,
                       time_bandwidth=time_bandwidth, return_itc=False)

# Plot visual gamma :)
power.plot([0], baseline=(-1.5, 0.),fmin=40,tmin=-1.5,tmax=1.5, mode='mean',
           title='RS Visual Gamma Occipital Sensor')













