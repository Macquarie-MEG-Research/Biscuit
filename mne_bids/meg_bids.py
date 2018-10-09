# Authors: Mainak Jas <mainak.jas@telecom-paristech.fr>
#          Alexandre Gramfort <alexandre.gramfort@telecom-paristech.fr>
#          Teon Brooks <teon.brooks@gmail.com>
#          Chris Holdgraf <choldgraf@berkeley.edu>
#
# License: BSD (3-clause)

import os
import os.path as op
from errno import EEXIST
import shutil as sh
import pandas as pd
from collections import defaultdict, OrderedDict

import numpy as np
from mne import read_events, find_events
from mne.io.constants import FIFF
from mne.io.pick import channel_type
from mne.io import BaseRaw
from mne.channels.channels import _unit2human
from mne.externals.six import string_types

from datetime import datetime
from warnings import warn

from .pick import coil_type
from .utils import (make_bids_filename, make_bids_folders, age_on_date,
                    make_dataset_description, _write_json, make_readme)
from .io import _parse_ext, _read_raw

ALLOWED_KINDS = ['meg', 'ieeg']
orientation = {'.sqd': 'ALS', '.con': 'ALS', '.fif': 'RAS', '.gz': 'RAS',
               '.pdf': 'ALS', '.ds': 'ALS'}

units = {'.sqd': 'm', '.con': 'm', '.fif': 'm', '.gz': 'm', '.pdf': 'm',
         '.ds': 'cm'}

manufacturers = {'.sqd': 'KIT/Yokogawa', '.con': 'KIT/Yokogawa',
                 '.fif': 'Elekta', '.gz': 'Elekta', '.pdf': '4D Magnes',
                 '.ds': 'CTF'}

IGNORED_CHANNELS = defaultdict(lambda: [])
IGNORED_CHANNELS['KIT/Yokogawa'] = ['STI 014']

COORDINATE_FRAMES = {FIFF.FIFFV_COORD_UNKNOWN: 'Unknown',
                     FIFF.FIFFV_COORD_DEVICE: 'Device',
                     FIFF.FIFFV_COORD_ISOTRAK: 'Isotrak',
                     FIFF.FIFFV_COORD_HPI: 'HPI',
                     FIFF.FIFFV_COORD_HEAD: 'Head',
                     FIFF.FIFFV_COORD_MRI: 'MRI',
                     FIFF.FIFFV_COORD_MRI_SLICE: 'MRI Slice',
                     FIFF.FIFFV_COORD_MRI_DISPLAY: 'MRI Display',
                     FIFF.FIFFV_COORD_DICOM_DEVICE: 'DICOM Device',
                     FIFF.FIFFV_COORD_IMAGING_DEVICE: 'Imaging Device'}


def _channels_tsv(raw, fname, verbose, manufacturer, overwrite):
    """Create channel tsv."""
    map_chs = defaultdict(lambda: 'OTHER')
    map_chs.update(meggradaxial='MEGGRADAXIAL',
                   megrefgradaxial='MEGREFGRADAXIAL',
                   meggradplanar='MEGGRADPLANAR',
                   megmag='MEGMAG', megrefmag='MEGREFMAG',
                   eeg='EEG', misc='MISC', stim='TRIG', emg='EMG',
                   ecog='ECOG', seeg='SEEG', eog='EOG', ecg='ECG')
    map_desc = defaultdict(lambda: 'Other type of channel')
    map_desc.update(meggradaxial='Axial Gradiometer',
                    megrefgradaxial='Axial Gradiometer Reference',
                    meggradplanar='Planar Gradiometer',
                    megmag='Magnetometer',
                    megrefmag='Magnetometer Reference',
                    stim='Trigger', eeg='ElectroEncephaloGram',
                    ecog='Electrocorticography',
                    seeg='StereoEEG',
                    ecg='ElectroCardioGram',
                    eog='ElectrOculoGram',
                    emg='ElectroMyoGram',
                    misc='Miscellaneous')
    get_specific = ('mag', 'ref_meg', 'grad')

    ignored_indexes = []
    for ch_name in IGNORED_CHANNELS[manufacturer]:
        if ch_name in raw.ch_names:
            ignored_indexes.append(raw.ch_names.index(ch_name))

    status, ch_type, description = list(), list(), list()
    for idx, ch in enumerate(raw.info['ch_names']):
        status.append('bad' if ch in raw.info['bads'] else 'good')
        _channel_type = channel_type(raw.info, idx)
        if _channel_type in get_specific:
            _channel_type = coil_type(raw.info, idx)
        ch_type.append(map_chs[_channel_type])
        description.append(map_desc[_channel_type])
    low_cutoff, high_cutoff = (raw.info['highpass'], raw.info['lowpass'])
    units = [_unit2human.get(ich['unit'], 'n/a') for ich in raw.info['chs']]
    n_channels = raw.info['nchan']
    sfreq = raw.info['sfreq']

    df = pd.DataFrame(OrderedDict([
                      ('name', raw.info['ch_names']),
                      ('type', ch_type),
                      ('units', units),
                      ('description', description),
                      ('sampling_frequency', ['%.2f' % sfreq] * n_channels),
                      ('low_cutoff', ['%.2f' % low_cutoff] * n_channels),
                      ('high_cutoff', ['%.2f' % high_cutoff] * n_channels),
                      ('status', status)]))
    df.drop(ignored_indexes, inplace=True)
    if not os.path.exists(fname) or overwrite is True:
        df.to_csv(fname, sep='\t', index=False)
    else:
        # maybe just raise error with no text and pick them all up later?
        raise ValueError('"%s" already exists. Please set overwrite to'
                         ' True.' % fname)

    if verbose:
        print(os.linesep + "Writing '%s'..." % fname + os.linesep)
        print(df.head())

    return fname


def _events_tsv(events, raw, fname, event_id, verbose, overwrite):
    """Create tsv file for events."""

    first_samp = raw.first_samp
    sfreq = raw.info['sfreq']
    events[:, 0] -= first_samp

    df = pd.DataFrame(np.c_[events[:, 0], np.zeros(events.shape[0]),
                            events[:, 2]],
                      columns=['onset', 'duration', 'condition'])
    if event_id:
        event_id_map = {v: k for k, v in event_id.items()}
        df.condition = df.condition.map(event_id_map)
    df.onset /= sfreq
    df = df.fillna('n/a')
    if not os.path.exists(fname) or overwrite is True:
        df.to_csv(fname, sep='\t', index=False)
    else:
        # maybe just raise error with no text and pick them all up later?
        raise ValueError('"%s" already exists. Please set overwrite to'
                         ' True.' % fname)

    if verbose:
        print(os.linesep + "Writing '%s'..." % fname + os.linesep)
        print(df.head())

    return fname


def _participants_tsv(raw, subject_id, group, fname, write_mode='append',
                      verbose=True):
    """Create a participants.tsv file and save it.

    This will append any new participant data to the current list if it
    exists. Otherwise a new file will be created with the provided information.

    Parameters
    ----------
    raw : instance of Raw
        The data as MNE-Python Raw object.
    subject_id : str
        The subject name in BIDS compatible format ('01', '02', etc.)
    group : str
        Name of group participant belongs to.
    fname : str
        Filename to save the participants.tsv to.
    write_mode : str, one of ('append', 'overwrite', 'error')
        How the file should be handled if is exists already.
        Defaults to 'append'.
        If write_mode == `append` the previously existing file will have the
        new data added to it, overwriting any duplicate entries found.
        If write_mode == `overwrite` the previously existing file will be
        removed and replaced with the new data.
        If write_mode == `error` an `OSError` will be raised.
    verbose : bool
        Set verbose output to true or false.

    """
    if op.exists(fname) and write_mode == 'error':
        raise OSError(EEXIST, '"%s" already exists. Please set'
                      ' write_mode to "overwrite" or "append".' % fname)

    subject_id = 'sub-' + subject_id
    data = {'participant_id': [subject_id]}

    subject_info = raw.info['subject_info']
    if subject_info is not None:
        genders = {0: 'U', 1: 'M', 2: 'F'}
        sex = genders[subject_info.get('sex', 0)]

        # determine the age of the participant
        age = subject_info.get('birthday', None)
        meas_date = raw.info.get('meas_date', None)
        if isinstance(meas_date, (tuple, list, np.ndarray)):
            meas_date = meas_date[0]

        if meas_date is not None and age is not None:
            bday = datetime(age[0], age[1], age[2])
            meas_datetime = datetime.fromtimestamp(meas_date)
            subject_age = age_on_date(bday, meas_datetime)
        else:
            subject_age = "n/a"

        data.update({'age': [subject_age], 'sex': [sex], 'group': [group]})

    # append the participant data to the existing file if it exists, otherwise
    # if `write_mode == 'overwrite'` write the data to a new file.
    if os.path.exists(fname) and write_mode == 'append':
        df = pd.read_csv(fname, sep='\t')
        df = df.append(pd.DataFrame(data=data,
                                    columns=['participant_id', 'age',
                                             'sex', 'group']))
        df.drop_duplicates(subset='participant_id', keep='last',
                           inplace=True)
        df = df.sort_values(by='participant_id')
    else:
        df = pd.DataFrame(data=data,
                          columns=['participant_id', 'age', 'sex',
                                   'group'])

    df.to_csv(fname, sep='\t', index=False, na_rep='n/a')

    if verbose:
        print(os.linesep + "Writing '%s'..." % fname + os.linesep)
        print(df.head())

    return fname


def _scans_tsv(raw, raw_fname, fname, verbose):
    """Create tsv file for scans."""

    meas_date = raw.info['meas_date']
    if isinstance(meas_date, (np.ndarray, list)):
        meas_date = meas_date[0]

    if meas_date is None:
        acq_time = 'n/a'
    else:
        acq_time = datetime.fromtimestamp(
            meas_date[0]).strftime('%Y-%m-%dT%H:%M:%S')

    # check to see if the file already exists.
    # If it does we will want to determine whether or not the data
    # is already there, and if not append it.
    if os.path.exists(fname):
        df = pd.read_csv(fname, sep='\t')
        df = df.append(pd.DataFrame(data={'filename': ['%s' % raw_fname],
                                          'acq_time': [acq_time]},
                                    columns=['filename', 'acq_time']))
        df.drop_duplicates(subset='filename', keep='last', inplace=True)
        df = df.sort_values(by='acq_time')
    else:
        df = pd.DataFrame(data={'filename': ['%s' % raw_fname],
                                'acq_time': [acq_time]},
                          columns=['filename', 'acq_time'])

    df.to_csv(fname, sep='\t', index=False)

    if verbose:
        print(os.linesep + "Writing '%s'..." % fname + os.linesep)
        print(df.head())

    return fname


def _coordsystem_json(raw, unit, orient, manufacturer, fname, verbose,
                      overwrite):
    dig = raw.info['dig']
    coords = dict()
    fids = {d['ident']: d for d in dig if d['kind'] ==
            FIFF.FIFFV_POINT_CARDINAL}
    if fids:
        if FIFF.FIFFV_POINT_NASION in fids:
            coords['NAS'] = fids[FIFF.FIFFV_POINT_NASION]['r'].tolist()
        if FIFF.FIFFV_POINT_LPA in fids:
            coords['LPA'] = fids[FIFF.FIFFV_POINT_LPA]['r'].tolist()
        if FIFF.FIFFV_POINT_RPA in fids:
            coords['RPA'] = fids[FIFF.FIFFV_POINT_RPA]['r'].tolist()

    hpi = {d['ident']: d for d in dig if d['kind'] == FIFF.FIFFV_POINT_HPI}
    if hpi:
        for ident in hpi.keys():
            coords['coil%d' % ident] = hpi[ident]['r'].tolist()

    coord_frame = set([dig[ii]['coord_frame'] for ii in range(len(dig))])
    if len(coord_frame) > 1:
        err = 'All HPI and Fiducials must be in the same coordinate frame.'
        raise ValueError(err)

    fid_json = {'MEGCoordinateSystem': orient,
                'MEGCoordinateUnits': unit,  # XXX validate this
                'HeadCoilCoordinates': coords,
                'HeadCoilCoordinateSystem': orient,
                'HeadCoilCoordinateUnits': unit  # XXX validate this
                }
    if not os.path.exists(fname) or overwrite is True:
        _write_json(fid_json, fname)
    else:
        # maybe just raise error with no text and pick them all up later?
        raise ValueError('"%s" already exists. Please set overwrite to'
                         ' True.' % fname)

    return fname


def _channel_json(raw, task, manufacturer, fname, kind, verbose, overwrite,
                  **extra_data):
    """ Sidecar json """

    sfreq = raw.info['sfreq']
    rectime = int(round(raw.times[-1]))      # for continuous data I think...
    powerlinefrequency = raw.info.get('line_freq', None)
    if powerlinefrequency is None:
        warn('No line frequency found, defaulting to 50 Hz')
        powerlinefrequency = 50

    # determine if there are any software filters
    software_filters = dict()
    for p_history in raw.info['proc_history']:
        max_info = p_history.get('max_info')
        if max_info:
            if max_info.get('max_st') != dict():
                software_filters['TSSS'] = {'Correlation':
                                            max_info['max_st']['subspcorr']}
            if max_info.get('sss_info') != dict():
                sss_info = {'frame':
                            COORDINATE_FRAMES[max_info['sss_info']['frame']]}
                software_filters['SSS'] = sss_info
    if software_filters == dict():
        software_filters = 'n/a'

    # see if the dewar angle is in the file
    gantry_angle = extra_data.get("DewarPosition", "XXX")
    if raw.info['gantry_angle'] is not None:
        gantry_angle = str(raw.info['gantry_angle']) + ' degrees'

    # determine whether any channels have to be ignored:
    num_ignored = 0
    for ch_name in IGNORED_CHANNELS[manufacturer]:
        if ch_name in raw.ch_names:
            num_ignored += 1
    # all ignored channels are trigger channels at the moment...

    n_megchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_MEG_CH])
    n_megrefchan = len([ch for ch in raw.info['chs']
                        if ch['kind'] == FIFF.FIFFV_REF_MEG_CH])
    n_eegchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_EEG_CH])
    n_ecogchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_ECOG_CH])
    n_seegchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_SEEG_CH])
    n_eogchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_EOG_CH])
    n_ecgchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_ECG_CH])
    n_emgchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_EMG_CH])
    n_miscchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_MISC_CH])
    n_stimchan = len([ch for ch in raw.info['chs']
                     if ch['kind'] == FIFF.FIFFV_STIM_CH]) - num_ignored

    # Define modality-specific JSON dictionaries
    ch_info_json_common = [
        ('TaskName', task),
        ('Manufacturer', manufacturer),
        ('PowerLineFrequency', powerlinefrequency)]
    ch_info_json_meg = [
        ('SamplingFrequency', sfreq),
        ("DewarPosition", gantry_angle),
        ("DigitizedLandmarks", extra_data.get("DigitizedLandmarks", False)),
        ("DigitizedHeadPoints", extra_data.get("DigitizedHeadPoints", False)),
        ("SoftwareFilters", software_filters),
        ('MEGChannelCount', n_megchan),
        ('MEGREFChannelCount', n_megrefchan)]
    ch_info_json_ieeg = [
        ('ECOGChannelCount', n_ecogchan),
        ('SEEGChannelCount', n_seegchan)]
    ch_info_ch_counts = [
        ('EEGChannelCount', n_eegchan),
        ('EOGChannelCount', n_eogchan),
        ('ECGChannelCount', n_ecgchan),
        ('EMGChannelCount', n_emgchan),
        ('MiscChannelCount', n_miscchan),
        ('TriggerChannelCount', n_stimchan)]
    ch_info_misc = [
        ('RecordingDuration', rectime),
        ('ContinuousHeadLocalization', False)]

    # maybe don't worry about this for now...
    if extra_data.get('emptyroom', None) is not None:
        ch_info_misc.append(('AssociatedEmptyRoom',
                             extra_data.get('emptyroom')))

    # Stitch together the complete JSON dictionary
    ch_info_json = []
    for field in ['InstitutionName', 'ManufacturersModelName',
                  'DeviceSerialNumber']:
        data = extra_data.get(field, None)
        if data is not None:
            ch_info_json.append((field, data))
    ch_info_json += ch_info_json_common
    append_kind_json = ch_info_json_meg if kind == 'meg' else ch_info_json_ieeg
    ch_info_json += append_kind_json
    ch_info_json += ch_info_ch_counts
    ch_info_json += ch_info_misc
    ch_info_json = OrderedDict(ch_info_json)

    if not os.path.exists(fname) or overwrite is True:
        _write_json(ch_info_json, fname, verbose=verbose)
    else:
        # maybe just raise error with no text and pick them all up later?
        raise ValueError('"%s" already exists. Please set overwrite to'
                         ' True.' % fname)

    return fname


def raw_to_bids(subject_id, task, raw_file, output_path, session_id=None,
                acquisition=None, run=None, kind='meg', events_data=None,
                event_id=None, hpi=None, electrode=None, hsp=None,
                emptyroom=False, config=None, overwrite=True, verbose=False,
                extra_data=dict(), subject_group='n/a', readme_text=None):
    """Walk over a folder of files and create bids compatible folder.

    Parameters
    ----------
    subject_id : str
        The subject name in BIDS compatible format (01, 02, etc.)
    task : str
        The task name.
    raw_file : str | instance of mne.Raw
        The raw data. If a string, it is assumed to be the path to the raw data
        file. Otherwise it must be an instance of mne.Raw
    output_path : str
        The path of the BIDS compatible folder
    session_id : str | None
        The session name in BIDS compatible format.
    acquisition : str | None
        The acquisition data identifier
    run : int | None
        The run number for this dataset.
    kind : str, one of ('meg', 'ieeg')
        The kind of data being converted. Defaults to "meg".
    events_data : str | array | None
        The events file. If a string, a path to the events file. If an array,
        the MNE events array (shape n_events, 3). If None, events will be
        inferred from the stim channel using `find_events`.
    event_id : dict
        The event id dict
    hpi : None | str | list of str
        Marker points representing the location of the marker coils with
        respect to the MEG Sensors, or path to a marker file.
        If list, all of the markers will be averaged together.
    electrode : None | str
        Digitizer points representing the location of the fiducials and the
        marker coils with respect to the digitized head shape, or path to a
        file containing these points.
    hsp : None | str | array, shape = (n_points, 3)
        Digitizer head shape points, or path to head shape file. If more than
        10`000 points are in the head shape, they are automatically decimated.
    emptyroom : bool | str
        Whether or not the supplied file is for the empty room measurement
        If False we do nothing.
        If True the file is used as an empty room file and handled correctly
        If a string is provided it is assumed that this is the file path to
        the associated empty room file.
    config : str | None
        A path to the configuration file to use if the data is from a BTi
        system.
    overwrite : True | bool | string
        Whether or not to overwrite the produced json, tsv files and any copied raw data.
        To avoid overwriting existing folders setting this to True will only overwrite
        the files.
    verbose : bool
        If verbose is True, this will print a snippet of the sidecar files. If
        False, no content will be printed.
    extra_data : dictionary
        A dictionary containing any extra information required to populate the
        json files.
        Currently supported keys are:
        'InstitutionName', 'ManufacturersModelName','DewarPosition',
        'Name' (Name of the project), 'DeviceSerialNumber'
    subject_group : string
        the group within the study the participant belongs to.
    readme_text : string
        A string containing the contents of the readme file to be placed along
        side the data.
    """
    if isinstance(raw_file, string_types):
        # We must read in the raw data
        raw = _read_raw(raw_file, electrode=electrode, hsp=hsp, hpi=hpi,
                        config=config, verbose=verbose)
        _, ext = _parse_ext(raw_file, verbose=verbose)
        raw_fname = raw_file
    elif isinstance(raw_file, BaseRaw):
        # Only parse the filename for the extension
        # Assume that if no filename attr exists, it's a fif file.
        raw = raw_file
        if hasattr(raw, 'filenames'):
            _, ext = _parse_ext(raw.filenames[0], verbose=verbose)
        else:
            ext = '.fif'
        raw_fname = raw.filenames[0]
    else:
        raise ValueError('raw_file must be an instance of str or BaseRaw, '
                         'got %s' % type(raw_file))

    if isinstance(hpi, string_types):
        # convert to a list for brevity later
        hpi = [hpi]

    if isinstance(emptyroom, string_types):
        extra_data['emptyroom'] = emptyroom
    elif emptyroom is True:
        # session, subject and task are all specified by the bids format
        session_id = datetime.fromtimestamp(
            raw.info['meas_date'][0]).strftime('%Y%m%d')
        subject_id = 'emptyroom'
        task = 'noise'
        acquisition = None    # set back to None so it isn't displayed

    """
    # do some sanitzation of the participant data provided:
    try:
        age = int(participant_data['age'])
    except (KeyError, ValueError):
        age = 'n/a'
    participant_data['age'] = age
    gender = participant_data.get('gender', 'n/a')
    if gender not in ['M', 'F', 'O']:
        gender = 'n/a'
    participant_data['gender'] = gender
    participant_data['group'] = participant_data.get('group', 'n/a')
    """

    # this will only work if the user specifies the electrode and hsp files,
    # which you wouldn't normally do if you just provide a raw
    # If raw files were to store all the paths we wouldn't need to do this
    # (other than empty room override...)
    extra_data["DigitizedLandmarks"] = (True if (electrode is not None and
                                                 emptyroom is not True) else False)
    extra_data["DigitizedHeadPoints"] = (True if (hsp is not None and emptyroom is not True) else False)

    data_path = make_bids_folders(subject=subject_id, session=session_id,
                                  kind=kind, root=output_path,
                                  verbose=verbose)
    if session_id is None:
        ses_path = data_path
    else:
        ses_path = make_bids_folders(subject=subject_id, session=session_id,
                                     root=output_path,
                                     verbose=verbose)

    processing = None
    proc_history = raw.info['proc_history']
    if proc_history != []:
        sss = False
        tsss = False
        for ph in proc_history:
            max_info = ph.get('max_info')
            if max_info:
                if (max_info['sss_info'] != dict() or
                        max_info['sss_ctc'] != dict() or
                        max_info['sss_cal'] != dict()):
                    sss = True
                if max_info['max_st'] != dict():
                    tsss = True
        if tsss:
            processing = 'tsss'
        elif sss:
            processing = 'sss'

    # create filenames
    scans_fname = make_bids_filename(
        subject=subject_id, session=session_id, suffix='scans.tsv',
        prefix=ses_path)
    participants_fname = make_bids_filename(prefix=output_path,
                                            suffix='participants.tsv')
    coordsystem_fname = make_bids_filename(
        subject=subject_id, session=session_id, acquisition=acquisition,
        suffix='coordsystem.json', prefix=data_path)
    data_meta_fname = make_bids_filename(
        subject=subject_id, session=session_id, task=task, run=run,
        processing=processing, acquisition=acquisition,
        suffix='%s.json' % kind, prefix=data_path)
    if ext in ['.fif', '.gz', '.ds']:
        raw_file_bids = make_bids_filename(
            subject=subject_id, session=session_id, task=task, run=run,
            acquisition=acquisition, processing=processing,
            suffix='%s%s' % (kind, ext))
    else:
        raw_folder = make_bids_filename(
            subject=subject_id, session=session_id, task=task, run=run,
            acquisition=acquisition, suffix='%s' % kind)
        raw_file_bids = make_bids_filename(
            subject=subject_id, session=session_id, task=task, run=run,
            acquisition=acquisition, suffix='%s%s' % (kind, ext),
            prefix=raw_folder)
    events_tsv_fname = make_bids_filename(
        subject=subject_id, session=session_id, task=task, run=run,
        acquisition=acquisition, suffix='events.tsv', prefix=data_path)
    channels_fname = make_bids_filename(
        subject=subject_id, session=session_id, task=task, run=run,
        acquisition=acquisition, suffix='channels.tsv', prefix=data_path)

    # Read in Raw object and extract metadata from Raw object if needed
    if kind == 'meg':
        orient = orientation[ext]
        unit = units[ext]
        manufacturer = manufacturers[ext]
    else:
        orient = 'n/a'
        unit = 'n/a'
        manufacturer = 'n/a'

    # save stuff
    if kind == 'meg':
        _scans_tsv(raw, os.path.join(kind, raw_file_bids), scans_fname,
                   verbose)
        if emptyroom is not True:
            _coordsystem_json(raw, unit, orient, manufacturer,
                              coordsystem_fname, verbose, overwrite)

    make_dataset_description(output_path, name=extra_data.get("Name", " "),
                             verbose=verbose)
    if isinstance(readme_text, string_types):
        make_readme(output_path, readme_text)
    if emptyroom is not True:
        _participants_tsv(raw, subject_id, subject_group, participants_fname,
                          'append', verbose)
    _channel_json(raw, task, manufacturer, data_meta_fname, kind, verbose,
                  overwrite, **extra_data)

    # set the raw file name to now be the absolute path to ensure the files
    # are placed in the right location
    raw_file_bids = os.path.join(data_path, raw_file_bids)

    # for FIF, we need to re-save the file to fix the file pointer
    # for files with multiple parts
    if ext in ['.fif', '.gz']:
        """
        make_bids_folders(subject=subject_id, session=session_id, kind=kind,
                          root=os.path.join('derivatives', output_path),
                          verbose=verbose)
        """
        raw.save(raw_file_bids, overwrite=overwrite)
    else:
        if os.path.exists(raw_file_bids):
            if overwrite:
                os.remove(raw_file_bids)
                sh.copyfile(raw_fname, raw_file_bids)
            else:
                raise ValueError('"%s" already exists. Please set overwrite to'
                                 ' True.' % raw_file_bids)
        else:
            # ensure the sub-folder exists
            if not os.path.exists(os.path.dirname(raw_file_bids)):
                os.makedirs(os.path.dirname(raw_file_bids))
            if ext == '.ds':
                # it is actually a folder and we need to copy the whole thing
                sh.copytree(raw_fname, raw_file_bids)
            else:
                # copy the file
                sh.copyfile(raw_fname, raw_file_bids)

    # empty room data doesn't require much...
    if emptyroom is not True:
        # copy the marker data
        if hpi is not None:
            # hpi is guaranteed to be a list
            for marker_path in hpi:
                _, marker_ext = _parse_ext(marker_path, verbose=verbose)
                marker_fname = make_bids_filename(
                    subject=subject_id, session=session_id, task=task, run=run,
                    acquisition=acquisition,
                    suffix='%s%s' % ('markers', marker_ext),
                    prefix=os.path.join(data_path, raw_folder))
                sh.copyfile(marker_path, marker_fname)

        _channels_tsv(raw, channels_fname, verbose, manufacturer, overwrite)

        events = _read_events(events_data, raw)
        if len(events) > 0:
            _events_tsv(events, raw, events_tsv_fname, event_id, verbose,
                        overwrite)

        # check to see if there is a headspace (hsp) or electrode placement
        # (electrode) provided.
        # if so, copy it to the correct location
        for f in (electrode, hsp):
            if f is not None:
                headshape_fname = make_bids_filename(
                    subject=subject_id, session=session_id,
                    suffix='headshape%s' % os.path.splitext(f)[1],
                    prefix=data_path)
                sh.copyfile(f, headshape_fname)

    return output_path


def _read_events(events_data, raw):
    """Read in events data."""
    if isinstance(events_data, string_types):
        events = read_events(events_data).astype(int)
    elif isinstance(events_data, np.ndarray):
        if events_data.ndim != 2:
            raise ValueError('Events must have two dimensions, '
                             'found %s' % events.ndim)
        if events_data.shape[1] != 3:
            raise ValueError('Events must have second dimension of length 3, '
                             'found %s' % events.shape[1])
        events = events_data
    else:
        #events = find_events(raw, stim_channel='STI 014')   #min_duration=0.001)
        events = find_events(raw, min_duration=0.002, initial_event=True)
    return events
