# this will take a bunch of info an reformat all the data to be compliant with the BIDS format
# we are interested in MEG data here, so we consider the MEG specifications for the BIDS format:

import mne
#from mne_bids import raw_to_bids
import os.path as path
from os import listdir, scandir
from sys import version_info
from datetime import datetime, date

def process_folder(folder, prefix='', validate=False):
    """
    Takes folder and prefix and returns the list of all files in the folder
    sorted by file type.
    The files returned are just the file names, not absolute paths.
    If the absolute path is required call os.path.join(folder, filename).

    Inputs:
    - folder | string
    - prefix | string or ''
        If prefix is an empty string, then return a dictionary where the keys are
        all the found prefixes
    - validate | bool
        If validate is true then return a boolean along with the dictionary indicating the validity of the folder

    Returns:
    - dictionary with keys in ('.con', '.mrk', '.elp', '.hsp', '.mri'), and values being
      lists of all files in the directory that have the specified file type and prefix.
    """

    # might want to make this a class so we can have the file verification process
    # separately accessable as this function could be useful for the GUI to have access to
    # for now will just process the entire folder, but it will be a little slower

    dtypes = {'.con':[],
              '.mrk':[],
              '.elp':[],
              '.hsp':[],
              '.mri':[]}

    if prefix == '':
        files = dict()
        prefixes = []
        for file in scandir(folder):
            if file.name.endswith('.elp'):
                prefixes.append(splitname(file.name)[0])
        for prefix in prefixes:
            files[prefix] = dtypes
    else:
        files = {prefix:dtypes}

    for prefix in files:
        for file in scandir(folder):
            if file.name.startswith(prefix) and splitname(file.name)[1] in dtypes.keys():
                files[prefix][splitname(file.name)[1]].append(file)

    if validate:
        valid = True
        # validate the folder:
        if len(files) == 0:
            valid = False
        else:
            for prefix in files:
                for dtype in files[prefix]:
                    if dtype != '.mri':
                        if len(files[prefix][dtype]) == 0:
                            valid = False
                            break
        return files, valid
    else:
        return files


def splitname(filename):
    # wrapper for the os.path.splitext function to allow for multiple python
    # versions
    if version_info.major == 3 and version_info.minor >= 6:
        # running 3.6 or higher
        return path.splitext(filename)
    else:
        return path.splitext(path.join(filename))


if __name__ == "__main__":
    # personal laptop paths
    p = "C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt\\2630_RS_PI160_2017_08_04"
    #p = 'C:\\Users\\msval\\Desktop\\rs_test_data_for_matt\\2630_RS_PI160_2017_08_04'
    #print(process_folder(p, '2630_RS_PI160_2017_08_04'))

    a = mne.io.read_raw_kit(path.join(p, '2630_RS_PI160_2017_08_04_B2.con'),
                            mrk = path.join(p, '2630_RS_PI160_2017_08_04_preB2.mrk'),
                            elp = path.join(p, '2630_RS_PI160_2017_08_04.elp'),
                            hsp = path.join(p, '2630_RS_PI160_2017_08_04.hsp'))
    subject_info = dict()
    #print(a.info)
    #a.info[]
    #print(subject_info)
    subject_info['id'] = 1234
    b = subject_info['birthday'] = (2000, 1, 2)
    subject_info['sex'] = 2
    a.info['subject_info'] = subject_info

    #p = a.plot()
    #p.show()
    #print(a.info['line_freq'])
    #print(isinstance(a, mne.io.Raw)
    #f = date.fromtimestamp(a.info['meas_date'])
    #g = date(b[0], b[1], b[2])
    print(len(a.info['dig']))
    #print(a.info['subject_info'])
    #print(f)
    #print(g)
    #k = f - g
    #print(k.days//365)
    #print(a.info['hpi_results'])
    #print(a.info['hpi_subsystem'])
    #raw_to_bids('CONTROL01', 'TASK01', a, path.join(p, 'newpath'), session_id='01', run=1)