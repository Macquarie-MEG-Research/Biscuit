# post-process some of the BIDS files produced to add any extra data we want

from collections import OrderedDict as odict
import json
import os
import os.path as op
import shutil


from Biscuit.utils.utils import get_mrk_meas_date
from bidshandler.utils import _get_bids_params, _bids_params_are_subsets
from mne_bids import BIDSPath

import pandas as pd


def clean_emptyroom(fpath):
    """Clean the directory containing the empty room data to only include the
    file required (sidecar and raw data)
    """
    # keep anything ending in `_meg`
    for fname in os.listdir(fpath):
        name = op.splitext(fname)[0]
        if not name.endswith('_meg'):
            os.remove(op.join(fpath, fname))


def modify_dataset_description(fname, name):
    with open(fname, 'r') as file:
        data = json.load(file, object_hook=odict)
    data['Name'] = name
    json_output = json.dumps(data, indent=4)
    with open(fname, 'w') as file:
        file.write(json_output)
        file.write('\n')


def update_markers(confile, fpath, bids_name):
    # TODO: shouldn't be needed once PR goes through on github
    """Update the markers provided and ensure that the BIDS output contains
    all the markers."""

    bids_params = _get_bids_params(bids_name)
    folder = os.path.split(fpath)[0]
    fnames = list(os.listdir(folder))   # cache for safety
    # do a check for any existing marker files with acq in their title
    for fname in fnames:
        params = _get_bids_params(fname)
        if params['file'] == 'markers':
            if params.get('acq', None) is not None:
                os.remove(op.join(folder, fname))
                continue

    if len(confile.hpi) != 2:
        # If there is only one marker for the con file we don't need to do
        # anything.
        return

    # First entry in the list will always be the one that gets converted.
    converted = confile.hpi[0]
    not_converted = confile.hpi[1]

    # determine which marker is pre and which is post
    confile.hpi.sort(key=get_mrk_meas_date)
    order = ['pre', 'post']
    if confile.hpi.index(converted) != 0:
        order = ['post', 'pre']

    fnames = list(os.listdir(folder))   # recache for safety
    for fname in fnames:
        params = _get_bids_params(fname)
        if params['file'] == 'markers':
            params['suffix'] = params.pop('file') + params.pop('ext')
            bids_path = BIDSPath(subject=params.get('sub', None),
                                       session=params.get('ses', None),
                                       run=params.get('run', None),
                                       task=params.get('task', None),
                                       suffix=params.get('suffix', None),
                                       acquisition=order[0])
            bname = bids_path.basename
            os.rename(op.join(folder, fname), op.join(folder, bname))
            bname = bname.replace('acq-{0}'.format(order[0]),
                                  'acq-{0}'.format(order[1]))
            shutil.copy(not_converted.file,
                        op.join(folder, op.basename(not_converted.file)))
            os.rename(op.join(folder, op.basename(not_converted.file)),
                      op.join(folder, bname))


def update_participants(fname, data):
    # add/modify the groups property
    df = pd.read_csv(fname, sep='\t')
    participant_id = data[0]
    group = data[1]
    if 'group' not in df:
        df = df.assign(group=[group])
    else:
        for i in range(len(df)):
            if df.loc[i, 'participant_id'] == participant_id:
                df.loc[i, 'group'] = group
    df.to_csv(fname, sep='\t', index=False, na_rep='n/a')


def update_sidecar(fname, data):
    # add dewar angle
    # modify the continuous head localisation value
    # add software filters
    # add empty room info
    # add serial number?
    with open(fname, 'r') as file:
        sidecar = json.load(file, object_hook=odict)

    new_data = odict()
    for key in ['InstitutionName', 'ManufacturersModelName',
                'DeviceSerialNumber', 'DewarPosition',
                'DigitizedLandmarks', 'DigitizedHeadPoints',
                'ContinuousHeadLocalization', 'AssociatedEmptyRoom']:
        if data.get(key, None) is not None:
            new_data[key] = data[key]
    new_output = odict()
    new_output.update(sidecar)
    for key, value in new_data.items():
        if key not in new_output:
            new_output.update({key: value})
        else:
            new_output[key] = value
    json_output = json.dumps(new_output, indent=4)
    with open(fname, 'w') as file:
        file.write(json_output)
        file.write('\n')


def write_readme(fname, readme_text):
    # Write the readme to the file.
    with open(fname, 'w') as file:
        file.write(readme_text)
