#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 09:46:57 2018

This script produces in the ALS co-ordinate system 

IMPORTANT: The units are transformed to METRES (m), not cm or mm

@author: Robert Seymour <robert.seymour@students.mq.edu.au>

Based largely on MNE functions written by:
- Teon Brooks <teon.brooks@gmail.com>
- Christian Brodbeck <christianbrodbeck@nyu.edu>

"""

import mne
import numpy as np
from mne.transforms import Transform
from mne.io.meas_info import _empty_info, _read_dig_points, _make_dig_points
from mne.coreg import fit_matched_points
from mne.io.kit import read_mrk
from six import string_types


def get_transform_mne(mrk, elp, hsp, bad_coil):
    """Add landmark points and head shape data to the KIT instance.

    Digitizer data (elp and hsp) are represented in [mm] in the Polhemus
    ALS coordinate system. This is converted to [m].

    Parameters
    ----------
    mrk : None | str | array_like, shape = (5, 3)
        Marker points representing the location of the marker coils with
        respect to the MEG Sensors, or path to a marker file.
    elp : None | str | array_like, shape = (8, 3)
        Digitizer points representing the location of the fiducials and the
        marker coils with respect to the digitized head shape, or path to a
        file containing these points.
    hsp : None | str | array, shape = (n_points, 3)
        Digitizer head shape points, or path to head shape file. If more
        than 10`000 points are in the head shape, the script raises on error.
    bad_coil : 
        Array containing the colors of the bad marker coils detected during
        recording. The array can contain up to two of the following:
        ['red','yellow','blue','white','black']

    Returns
    -------
    headshape       : list
        List of headshape points.
    trans           : dict
        A dictionary describe the device-head transformation.     
    three_cardinals : list
        List of cardinal co-ordinates (order: nasion,LPA,RPA)
    """
    if isinstance(hsp, string_types):
        hsp = _read_dig_points(hsp)
        
    n_pts = len(hsp) 
    if n_pts > 10000:
        raise ValueError("You need to reduce the number of headshape Polhemus"
                         "points to under 10,000")

    if isinstance(elp, string_types):
        elp_points = _read_dig_points(elp)
        if len(elp_points) != 8:
            raise ValueError("File %r should contain 8 points; got shape "
                             "%s." % (elp, elp_points.shape))
        elp = elp_points
    elif len(elp) != 8:
        raise ValueError("ELP should contain 8 points; got shape "
                         "%s." % (elp.shape,))
    if isinstance(mrk, string_types):
        mrk2 = read_mrk(mrk)

    # Get markers from elp file
    elp_markers = elp[3:]
    
    ###########################################################################
    # Take out any bad coils from mrk and elp data
    mrk_order = ['red','yellow','blue','white','black']
    
    # Raise error if there are more than two bad coils
    if len(bad_coil) > 2:
        raise ValueError("You need at least 3 good coils for a correct transform")
    
    # If any bad coils appear in the mrk_order list
    if any(s in bad_coil for s in mrk_order):
        indices = []
        # For each bad marker...
        for r in range(0,len(bad_coil),1):
            # Find where in the order list the bad marker is found...
            indices_spare = [i for i, f in enumerate(mrk_order) if bad_coil[r] in f]
            indices.append(indices_spare[0])
            print("TAKING OUT BAD MARKER: %s" % (bad_coil[r]))
        # Remove this information from the mrk and elp variables
        mrk2 = np.delete(mrk2,indices,0)
        elp_markers = np.delete(elp_markers,indices,0)
        
    ###########################################################################
        
    # device head transform
    trans = fit_matched_points(tgt_pts=elp_markers, src_pts=mrk2, out='trans')
    
    #nasion, lpa, rpa = elp[:3]
    #elp = elp[3:]
    
    three_cardinals = elp[:3] # nasion, LPA, RPA
    #dig_points = _make_dig_points(nasion, lpa, rpa, elp, hsp)
    headshape = hsp

    return headshape, trans, three_cardinals
