# post-process some of the BIDS files produced to add any extra data we want

from collections import OrderedDict as odict
import json
import os
import os.path as op

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


def update_markers(confile, fpath):
    # TODO: shouldn't be needed once PR goes through on github
    """Update the markers provided and ensure that the BIDS output contains
    all the markers."""
    print('updating markers')
    if len(confile.hpi.keys()) == 1:
        # If there is only one marker for the con file we don't need to do
        # anything.
        return
    converted = None
    not_converted = None
    for key, value in confile.hpi.items():
        if value == confile.converted_hpi:
            converted = key
        else:
            not_converted = key
    print(fpath)
    print(converted)
    print(not_converted)
    # take the currently existing marker file and add the correct `acq` value
    # copy the other marker file to the correct location with the correct name
    # also.


def update_participants(fname, data):
    # add/modify the groups property
    df = pd.read_csv(fname, sep='\t')
    participant_id = data[0]
    group = data[1]
    if 'group' not in df:
        df = df.assign(group=[group])
    else:
        for i in range(len(df)):
            if df.ix[i, 'participant_id'] == participant_id:
                df.ix[i, 'group'] = group
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
