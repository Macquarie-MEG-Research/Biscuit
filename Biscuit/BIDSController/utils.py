import os.path as op
import os
import shutil

import pandas as pd


def get_bids_params(fname):
    filename, ext = op.splitext(fname)
    f = filename.split('_')
    data = {'ext': ext}
    for i in f:
        if '-' in i:
            data[i.split('-')[0]] = i.split('-')[1]
        else:
            data['file'] = i
    return data


def bids_params_are_subsets(params1, params2):
    """Equivalent to asking if params1 >= params2."""
    param1_keys = set(params1.keys())
    param2_keys = set(params2.keys())
    for key in ['file', 'ext']:
        param1_keys = param1_keys - {key}
        param2_keys = param2_keys - {key}
    if param1_keys >= param2_keys:
        for key in param2_keys:
            if not params2[key] == params1[key]:
                return False
        return True
    return False


def combine_tsv(tsv, df, drop_column=None):
    """Merge a df into a tsv file"""
    orig_df = pd.read_csv(tsv, sep='\t')
    orig_df = orig_df.append(df)
    if drop_column is not None:
        orig_df.drop_duplicates(subset=drop_column, keep='last', inplace=True)
    orig_df.to_csv(tsv, sep='\t', index=False, na_rep='n/a', encoding='utf-8')


def copyfiles(src_files, dst_files):
    assert len(src_files) == len(dst_files)
    for fnum in range(len(src_files)):
        if not op.exists(op.dirname(dst_files[fnum])):
            os.makedirs(op.dirname(dst_files[fnum]), exist_ok=True)
        try:
            shutil.copy(src_files[fnum], dst_files[fnum])
        except shutil.SameFileError:
            # for now just skip files that are the same.
            print('same file!!')


# This could possibly be a method for the classes? If they become subclassed
# it would only need to be defined for the base class.
# this could also be a decorator taking the instance of the class as an arg
def realize_paths(obj, rel_paths):
    """Returns the actual path to a file.

    Parameters
    ----------
    obj : Instance of Project, Subject, Session or Scan
        The object the path will be found relative to.
    rel_path : str
        Relative path from an object

    """
    if isinstance(rel_paths, list):
        ret_paths = []
        for fpath in rel_paths:
            ret_paths.append(op.join(obj.path, fpath))
        return ret_paths
    return op.join(obj.path, rel_paths)


def splitall(path):
    # credit: Trent Mick:
    # https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
    allparts = []
    while 1:
        parts = op.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


if __name__ == "__main__":
    print(get_bids_params('sub-1111_ses-aab_scans.json'))
