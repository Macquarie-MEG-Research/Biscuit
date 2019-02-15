# post-process some of the BIDS files produced to add any extra data we want

from collections import OrderedDict as odict
import json

import pandas as pd


def clean_emptyroom(fpath):
    """Clean the directory containing the empty room data to only include the
    file required (sidecar and raw data)
    """
    pass


def modify_dataset_description(fname, name):
    with open(fname, 'r') as file:
        data = json.load(file, object_hook=odict)
    data['Name'] = name
    json_output = json.dumps(data, indent=4)
    with open(fname, 'w') as file:
        file.write(json_output)
        file.write('\n')


def update_participants(fname, data):
    # add/modify the groups property
    df = pd.read_csv(fname, sep='\t')
    participant_id = data[0]
    group = data[1]
    if 'group' not in df:
        if len(df) == 1:
            df.assign(group=[group])
        else:
            raise ValueError('Data provided is invalid')
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
