# merge BIDS-compatible folders

from os import walk, makedirs, rename, scandir
import os.path as path
import pandas as pd

from shutil import copy


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


def merge_proj(left, right, overwrite=False):
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
        # TODO: make better...
        raise ValueError("Some values already exist!!!")

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
        copy(src, dst)
        print('copied file to {0}'.format(dst))

    # merge the participants files:
    part_left = left_map.get('participants', [])
    part_right = right_map.get('participants', [])
    if len(part_left) == len(part_right) == 1:
        part_left = path.join(left, part_left[0])
        part_right = path.join(right, part_right[0])
        df_l = pd.read_csv(part_left, sep='\t')
        df_r = pd.read_csv(part_right, sep='\t')
        df_r = df_r.append(df_l)
        df_r.drop_duplicates(subset='participant_id', keep='last',
                             inplace=True)
        df_r = df_r.sort_values(by='participant_id')
        df_r.to_csv(part_right, sep='\t', index=False, na_rep='n/a')


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


left = ('C:\\Users\\MQ20184158\\Documents\\MEG data\\'
        'rs_test_data_for_matt\\BIDS-2018-21')

right = path.join(svr_path, 'BIDS')

proj_list = get_projects(left)
for proj_path in proj_list:
    merge_proj(path.join(left, proj_path), path.join(right, proj_path))

# TODO: write custom version fo shutil.copy to track progress

""" some code from shutil:

def copyfileobj(fsrc, fdst, length=16*1024):
    #copy data from file-like object fsrc to file-like object fdst
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)

def copyfile(src, dst, *, follow_symlinks=True):
    #Copy data from src to dst.

    #If follow_symlinks is not set and src is a symbolic link, a new
    #symlink will be created instead of copying the file it points to.

    if _samefile(src, dst):
        raise SameFileError("{!r} and {!r} are the same file".format(src, dst))

    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:
            # File most likely does not exist
            pass
        else:
            # XXX What about other special files? (sockets, devices...)
            if stat.S_ISFIFO(st.st_mode):
                raise SpecialFileError("`%s` is a named pipe" % fn)

    if not follow_symlinks and os.path.islink(src):
        os.symlink(os.readlink(src), dst)
    else:
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copyfileobj(fsrc, fdst)
    return dst


def copy(src, dst, *, follow_symlinks=True):
    #Copy data and mode bits ("cp src dst"). Return the file's destination.

    #The destination may be a directory.

    #If follow_symlinks is false, symlinks won't be followed. This
    #resembles GNU's "cp -P src dst".

    #If source and destination are the same file, a SameFileError will be
    #raised.

    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    copymode(src, dst, follow_symlinks=follow_symlinks)
    return dst

"""
