# merge BIDS-compatible folders

from os import walk, makedirs
import os.path as path

from shutil import copy

# TODO: move everything up a level (work on project-level, not below...)

svr_path = "\\\\file.cogsci.mq.edu.au\\Homes\\mq20184158"

PROCESSMAP = {'participants.tsv': 'participants',
              'scans.tsv': 'scans',
              'description.json': 'description',
              'coordsystem.json': 'coordsystem',
              'channels.tsv': 'channels',
              'events.tsv': 'events',
              'meg.json': 'sidecar',
              'markers.mrk': 'markers',
              'meg.con': 'raw',
              'README.txt': 'readme',
              'headshape.elp': 'elp',
              'headshape.hsp': 'hsp'}


def merge(left, right, overwrite=False):
    """ combine two bids-compatible folders

    Parameters
    ----------
    left : str
        The incoming folder.
    right : str
        Currently existing folder that left will be merged into.
        Most files will simply be copied over, however the participants.tsv
        and scans.tsv files will both be merged such that the data in both
        files is combined.
    overwrite : bool
        Whether or not to overwrite the currently existing data
        Defaults to False.

    """
    left_map = map_folder(left)
    right_map = map_folder(right)
    diff = list()
    # go over the left map and split it into two dictionaries.
    # One with values that *aren't* in the right_map, and leave those that
    # are in right_map in left_map.
    for key, value in left_map.items():
        for i in range(len(value) - 1, -1, -1):
            fpath = value[i]
            if fpath not in right_map[key]:
                diff.append(value.pop(i))
    # if there are no conflicts the only files left in the left_map should
    # be the participants and scans files which need to be merged separately,
    # and a readme.txt and dataset_description.json (which are copied over)
    # Any other remaining files will only be copied over if overwrite == True.
    conflicting_keys = []

    # check to see if there are any conflicting files
    for key, value in left_map.items():
        if key not in ['participants', 'scans', 'description', 'readme']:
            if len(value) != 0:
                conflicting_keys.append(key)

    print(conflicting_keys)

    # check for conflicts
    if not overwrite and len(conflicting_keys) != 0:
        # TODO: make better...
        raise ValueError("Some values already exist!!!")

    # now merge the data over that we need to.
    for fpath in diff:
        base = path.join(right, path.dirname(fpath))
        if not path.exists(base):
            makedirs(base)
        src = path.join(left, fpath)
        dst = path.join(right, fpath)
        copy(src, dst)
        print('copied file to {0}'.format(dst))


def map_folder(fpath):
    """ fpath is the path to the Project-level folder """
    data = dict()

    for root, _, files in walk(fpath):
        for file in files:
            base = path.relpath(root, fpath)
            relpath = path.join(base, file)
            for key, value in PROCESSMAP.items():
                if file.endswith(key):
                    update_or_add(data, value, relpath)
                    break
    return data


def update_or_add(d, key, value):
    if key not in d:
        d[key] = [value]
    else:
        d[key].append(value)


left = ('C:\\Users\\MQ20184158\\Documents\\MEG data\\'
        'rs_test_data_for_matt\\BIDS2\\WS001')

right = path.join(svr_path, 'BIDS', 'WS001')

merge(left, right)
