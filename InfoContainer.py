from tkinter import StringVar, IntVar, DoubleVar, BooleanVar, ACTIVE, DISABLED
from ToBIDS import process_folder
import datetime
from mne.io import read_raw_kit

from utils import *
from FileTypes import generic_file

"""
Will need to set up some system that we can specify whether the data is read from the Raw data from mne,
or if we have to read it ourselves.
Some data we may want to incorporate into the MNE library anyways, especially mne-bids
"""

####
"""
This need a huge overhaul!!!
"""
####


class InfoContainer():
    """
    Each MEG "object" that will be converted to BIDS format
    will have an associated InfoContainer object.
    This will contain all the relevant information to
    create a BIDS compatible file structure and associated
    files.
    """
    def __init__(self, id_, folder, parent):
        """
        Inputs:
        id_ - An automaticlaly generated id. This matches the id of the treeview entry associated with the file
        This will allow the InfoContainer to be easily and uniquely correlated with a specific folder in the treeview
        folder - The full file path to the folder containing the files
        parent - The parent gui application. This will be used to allow for the InfoContainer to make modifications on the gui itself (eg. for verification)
        
        """
        self._id = id_
        self.folder = folder
        self.parent = parent

        self.is_valid = False       # whether or not the folder contains all the required files
        self.is_bids_ready = False  # whether or not all the associated files have all the required data

        self.initialised = False    # whether or not the data has actually been initialised. This will be set
                                    # to true when self.initiate() is called

        self._process_folder()

        # this function needs to be modified to take in the parent id from the treeview instead
        # this way it can get the ids of the children files to associate with the FileInfo objects
        #self.contained_files, self.is_valid = process_folder(self.folder, validate=True)

        self._set_required_inputs()

        self.raw_files = dict()
        self.extra_data = dict()

        if self.is_valid and self.is_bids_ready:
            self.initiate()

    
    def initiate(self):
        # run any functions relating to generating Raw's, setting inputs etc, reading data etc.
        self._create_raws()
        #self._read_data()
        self.initialised = True

    def _process_folder(self):

        # probably will be better to construct the contained_files dictionary directly instead of filling an intermediatary object

        # this will automatically preload the data of any contained files
        files = {'.con':[],
                 '.mrk':[],
                 '.elp':[],
                 '.hsp':[],
                 '.mri':[]}

        # go through the direct children of the folder via the treeview
        for sid in self.parent.file_treeview.get_children(self._id):
            item = self.parent.file_treeview.item(sid)
            # check the extension of the file. If it is in the files dict, add the file to the list
            ext = item['values'][0]
            if ext in files:
                # generate the FileInfo subclass object
                cls_ = get_object_class(ext)
                if not isinstance(cls_, str):
                    # and only call it if it can be. str types are ignored (only other return type)
                    obj = cls_(sid, item['values'][1], self)
                    files[item['values'][0]].append(obj)
                    # also add the data to the preload data
                    if sid not in self.parent.preloaded_data:
                        self.parent.preloaded_data[sid] = obj
            else:
                cls_ = get_object_class(ext)
                if cls_ is not 'folder':
                    obj = cls_(sid, item['values'][1], self)
                    if isinstance(obj, generic_file):
                        obj.dtype = ext
                    else:
                        print(type(obj), obj, 'woowee!')
                    # we do not need to add it to the list of files, but add to the parent's preload data:
                    if sid not in self.parent.preloaded_data:
                        self.parent.preloaded_data[sid] = obj

        valid = True
        # validate the folder:
        for dtype, data in files.items():
            if dtype != '.mri':
                if len(data) == 0:
                    valid = False
                    break
        
        # we'll only check whether the folder is ready to be exported to bids format if it is valid
        if valid:
            # the bids verification is it's own function so it can be called externally by other objects such as the InfoManager
            self.check_bids_ready()

        self.contained_files = files
        self.is_valid = valid

    def _create_raws(self):
        print('creating raws')
        acqs = dict()
        for con_file in self.contained_files['.con']:
            acq = con_file.required_info['Acquisition'].get()
            if acq in acqs:
                acqs[acq].append(con_file)
            else:
                acqs[acq] = [con_file]
        
        for acq, con_files in acqs.items():
            print('generating acq {0}'.format(acq))
            if len(con_files) > 1:
                # in this case we will need to combine them somehow...
                # Let's figure this out later...
                pass
            elif len(con_files) == 1:
                # in this case we have a single con file per acq, and some number of mrk files
                self.raw_files[acq] = read_raw_kit(con_files[0].file,
                                                   mrk = [mrk_file.file for mrk_file in con_files[0].required_info['associated_mrks']],    # construct a list of the file paths
                                                   elp = self.contained_files['.elp'][0].file,        # we should only have 1 .elp...
                                                   hsp = self.contained_files['.hsp'][0].file)        # ... and one .hsp file in the folder
                # also populate the extra data dictionary so that it can be used when producing bids data
                self.extra_data[acq] = {'InstitutionName': con_files[0].info['Insitution name'],
                                        'ManufacturersModelName':con_files[0].info['Model name']}

    def check_bids_ready(self):
        """
        Check to see whether all contained files required to produce a bids-compatible
        file system have all the necessary data
        """
        print("checking to see if it is ready for bids-ification")
        if self.is_valid:
            for dtype, files in self.contained_files.items():
                for file in files:
                    bads = file.check_complete()
                    if bads != []:
                        self.parent.info_notebook.raw_gen_btn.config({"state":DISABLED})
                        return False
            print("Good to go!")
            self.parent.info_notebook.raw_gen_btn.config({"state":ACTIVE})
            return True
        else:
            print('not valid...')
            self.parent.info_notebook.raw_gen_btn.config({"state":DISABLED})
            return False

    """
    def other(self):
        # just storing this here for now...
        self.info['Date recorded'] = datetime.datetime.fromtimestamp(self.raw_files[0].info['meas_date'])
        self.info['measurement_length'] = ("Length of recording", self.raw_files[0].times[-1])
    """

    def _set_required_inputs(self):
        # we have a number of basic properties that we need:
        self.subject_ID = ("Subject ID", StringVar())
        self.task_name = ("Task name", StringVar())
        self.session_ID = ("Session ID", StringVar())

    def get(self, name):
        print(name)

    @property
    def ID(self):
        return self._id

    """
    def __getattr__(self, name):
        # Return None if no property is found with the given name
        return self.__dict__.get(name, None)
    """

    #def __repr__(self):
    #    return str(self._id) + ',' + str(self.folder)