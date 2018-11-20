# merge BIDS-compatible folders

from os import walk, makedirs, rename, scandir
import os.path as path
import pandas as pd
from hashlib import md5

from utils.copyutils import copy

SVR_PATH = "\\\\file.cogsci.mq.edu.au\\Homes\\mq20184158"
BUFFER_SIZE = 1024 * 1024     # 1Mb

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


def merge_proj(left, right, overwrite=False, file_name_tracker=None,
               file_num_tracker=None, file_prog_tracker=None):
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
    file_name_tracker : Instance of StringVar
        An instance of a tkinter.StringVar which has the filename of the
        current file being transfer. This is for tracking purposes in the
        Windows.SendFilesWindow window.
    file_num_tracker : Instance of IntVar
        An instance of a tkinter.IntVar which is incremented after each file
        has been transferred. This is for tracking purposes in the
        Windows.SendFilesWindow window.
    file_prog_tracker : Instance of IntVar
        An instance of a tkinter.IntVar which is used to track the transfer
        progress on a file-by-file basis. This is passed to the modified copy
        function from shutil to track  the rate at whic the indiviual files
        themselves are being transferred. This is for tracking purposes in the
        Windows.SendFilesWindow window.

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
            if fpath not in right_map.get(key, []):
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

    # check for conflicts
    if not overwrite and len(conflicting_keys) != 0:
        raise FileExistsError("Some values already exist!!!")

    # add the description and readme to the diff:
    desc = left_map.get('description', None)
    if desc:
        diff.append(desc[0])
    readme = left_map.get('readme', None)
    if readme:
        diff.append(readme[0])

    # now merge the data over that we need to.
    for fpath in diff:
        base = path.join(right, path.dirname(fpath))
        if not path.exists(base):
            makedirs(base)
        src = path.join(left, fpath)
        dst = path.join(right, fpath)
        # set the name *before* copying
        if file_name_tracker is not None:
            file_name_tracker.set(path.basename(src))
        _, file_hash = copy(src, dst, tracker=file_prog_tracker, verify=True)
        if file_hash.hexdigest() != md5hash(dst).hexdigest():
            raise ValueError("Copied file is different to source file.")
        if file_num_tracker is not None:
            file_num_tracker.set(file_num_tracker.get() + 1)

    # merge the participants files:
    part_left = left_map.get('participants', [])
    part_right = right_map.get('participants', [])
    if len(part_left) == len(part_right) == 1:
        if file_name_tracker is not None:
            file_name_tracker.set(part_left[0])
        part_left = path.join(left, part_left[0])
        part_right = path.join(right, part_right[0])
        df_l = pd.read_csv(part_left, sep='\t')
        df_r = pd.read_csv(part_right, sep='\t')
        df_r = df_r.append(df_l)
        df_r.drop_duplicates(subset='participant_id', keep='last',
                             inplace=True)
        df_r = df_r.sort_values(by='participant_id')
        df_r.to_csv(part_right, sep='\t', index=False, na_rep='n/a')
    file_name_tracker.set("Complete!")


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


def get_projects(fpath):
    """ Get a list of all projects within the specified bids folder """
    projects = []
    for f in scandir(fpath):
        if f.is_dir():
            projects.append(f.name)
    return projects


def rename_copied(fpath):
    """ rename the folder to have `_copied` appended to the name """
    rename(fpath, "{0}_copied".format(fpath))


def md5hash(src):
    """ Gets the md5 hash of a file in chunks """
    contents_hash = md5()
    with open(src, 'rb') as fsrc:
        while True:
            data = fsrc.read(BUFFER_SIZE)
            if not data:
                break
            contents_hash.update(data)
    return contents_hash


if __name__ == "__main__":

    left = ('C:\\Users\\MQ20184158\\Documents\\MEG data\\'
            'rs_test_data_for_matt\\BIDS-2018-21')

    right = path.join(SVR_PATH, 'BIDS')

    proj_list = get_projects(left)
    for proj_path in proj_list:
        merge_proj(path.join(left, proj_path), path.join(right, proj_path))
