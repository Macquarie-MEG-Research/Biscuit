from tkinter import StringVar, IntVar, ACTIVE, DISABLED
#from ToBIDS import process_folder
#import datetime
from mne.io import read_raw_kit
from mne.io.constants import FIFF

from OptionVars import StringOptsVar
from utils import flatten, get_object_class
from FileTypes import generic_file

"""
Will need to set up some system that we can specify whether the data is read
from the Raw data from mne,
or if we have to read it ourselves.
Some data we may want to incorporate into the MNE library anyways, especially
mne-bids
"""


class InfoContainer():
    """
    Each MEG "object" that will be converted to BIDS format
    will have an associated InfoContainer object.
    This will contain all the relevant information to
    create a BIDS compatible file structure and associated
    files.
    """
    def __init__(self, id_, file_path, parent, settings):
        """
        Inputs:
        id_ - An automaticlaly generated id. This matches the id of the
            treeview entry associated with the file
            This will allow the InfoContainer to be easily and uniquely
            correlated with a specific folder in the treeview
        file_path - The full file path to the folder containing the files
        parent - The parent gui application. This will be used to allow for
            the InfoContainer to make modifications on the gui itself
            (eg. for verification)
        settings - A list of disctionaries containing all the project settings
        """
        self._id = id_
        self.file_path = file_path
        self.parent = parent
        self.proj_settings = settings
        # just set as loaded always since we don't want a load_data() method
        # for this class
        self.loaded = True

        self.proj_name = StringVar()
        self.proj_name.trace("w", self._apply_settings)
        self.subject_group = StringOptsVar()

        # whether or not the folder contains all the required files
        self.is_valid = False
        # whether or not all the associated files have all the required data
        self.is_bids_ready = False

        # whether or not the data has actually been initialised.
        # This will be set to true when self.initiate() is called.
        self.initialised = False

        self._process_folder()

        # This function needs to be modified to take in the parent id from the
        # treeview instead.
        # This way it can get the ids of the children files to associate with
        # the FileInfo objects.
        if self.is_valid:
            self._set_required_inputs()

        self.raw_files = dict()
        self.extra_data = dict()
        self.acq_con_map = dict()

        if self.is_valid and self.is_bids_ready:
            self.initiate()

    def initiate(self):
        # run any functions relating to generating Raw's, setting inputs etc,
        # reading data etc.
        self._create_raws()
        #self._read_data()
        self.initialised = True

    def _process_folder(self):

        # probably will be better to construct the contained_files dictionary
        # directly instead of filling an intermediatary object

        # this will automatically preload the data of any contained files
        files = {'.con': [],
                 '.mrk': [],
                 '.elp': [],
                 '.hsp': [],
                 '.mri': []}

        # go through the direct children of the folder via the treeview
        for sid in self.parent.file_treeview.get_children(self._id):
            item = self.parent.file_treeview.item(sid)
            # check the extension of the file. If it is in the files dict, add
            # the file to the list
            ext = item['values'][0]
            # generate the FileInfo subclass object
            cls_ = get_object_class(ext)
            if not isinstance(cls_, str):
                # and only call it if it can be. str types are ignored
                # (only other return type)
                obj = cls_(sid, item['values'][1], self, auto_load=False,
                           treeview=self.parent.file_treeview)
                if isinstance(obj, generic_file):
                    obj.dtype = ext
                # only add to the 'files' variable if it needs to be
                if ext in files:
                    files[item['values'][0]].append(obj)
                # also add the data to the preload data
                if sid not in self.parent.preloaded_data:
                    self.parent.preloaded_data[sid] = obj

        valid = True
        # validate the folder:
        for dtype, data in files.items():
            if dtype != '.mri':
                if len(data) == 0:
                    valid = False
                    break

        # we'll only check whether the folder is ready to be exported to bids
        # format if it is valid
        if valid:
            # the bids verification is it's own function so it can be called
            # externally by other objects such as the InfoManager
            self.check_bids_ready()

        self.contained_files = files
        self.is_valid = valid

    def _create_raws(self):
        print('creating raws')
        # refresh to avoid adding the con files each time
        self.acq_con_map = dict()
        for con_file in self.contained_files['.con']:
            acq = con_file.acquisition.get()
            if con_file.is_junk.get() is False:
                if con_file.is_empty_room.get():
                    acq = 'emptyroom'
                if acq in self.acq_con_map:
                    self.acq_con_map[acq].append(con_file)
                else:
                    self.acq_con_map[acq] = [con_file]
            # otherwise we need to maybe copy them??

        for acq, con_files in self.acq_con_map.items():
            print('generating acq {0}'.format(acq))
            if len(con_files) > 1:
                # in this case we will need to combine them somehow...
                # Let's figure this out later...
                pass
            elif len(con_files) == 1:
                # in this case we have a single con file per acq, and some
                # number of mrk files
                if acq == 'emptyroom':
                    # in this case we don't have/need hsp, elp or mrk files:
                    self.raw_files[acq] = read_raw_kit(con_files[0].file)
                    # assign the raw file to the con file
                    con_files[0].associated_raw = self.raw_files[acq]
                else:
                    # we can read the triggers out first as we don't need to
                    # worry about the names
                    trigger_channels, _ = con_files[0].get_trigger_channels()
                    if trigger_channels == []:
                        trigger_channels = '>'
                        stim_code = 'binary'
                        slope = '-'
                    else:
                        stim_code = 'channel'
                        slope = '+'
                    print('trigger channels:', trigger_channels)
                    self.raw_files[acq] = read_raw_kit(
                        con_files[0].file,
                        # construct a list of the file paths
                        mrk=[mrk_file.file for mrk_file in 
                             con_files[0].associated_mrks],
                        elp=self.contained_files['.elp'][0].file,
                        hsp=self.contained_files['.hsp'][0].file,
                        stim=trigger_channels, stim_code=stim_code,
                        slope=slope)
                    con_files[0].associated_raw = self.raw_files[acq]
                    bads, name_mapping = self._get_channel_name_changes(
                        con_files[0])
                    # rename the channels
                    self.raw_files[acq].rename_channels(name_mapping)
                    # set the bads
                    self.raw_files[acq].info['bads'] = bads
                    # change the channel type of any channels that are triggers
                    if isinstance(trigger_channels, list):
                        for ch in trigger_channels:
                            i = int(ch) - 1
                            ch_info = self.raw_files[acq].info['chs'][i]
                            ch_info['kind'] = FIFF.FIFFV_STIM_CH
                    # assign the raw file to the con file
                    con_files[0].associated_raw = self.raw_files[acq]
                # Also populate the extra data dictionary so that it can be
                # used when producing bids data.
                # This requires the file to be loaded, so we will do that for
                # any files that happen to have not been loaded
                if con_files[0].loaded is False:
                    con_files[0].load_data()
                self.extra_data[acq] = {
                    'InstitutionName': con_files[0].info['Institution name'],
                    'ManufacturersModelName': 'KIT-160',
                    'DewarPosition': self.dewar_position.get(),
                    'Name': self.proj_name.get(),
                    'DeviceSerialNumber': con_files[0].info['Serial Number']}

    def _get_channel_name_changes(self, file):
        """
        Take the channel list and get any bad channels and set the channels in
        the associated raw as bad.
        Returns the list of bads and a dictionary describing the mapping of
        name mapping
        """
        bads = []
        name_mapping = dict()

        for ch_data in file.tab_info.values():
            if ch_data[1].get() == 1:
                bads.append(ch_data[0].get())

        for i, name in enumerate(file.channel_names):
            orig_name = file.associated_raw.info['ch_names'][i]
            name_mapping[orig_name] = name

        return bads, name_mapping

    def _get_trigger_channels(self, file):
        """ Returns the list of trigger channels associated with the data and
        the descriptions """
        trigger_channels = []
        descriptions = []
        for i in range(len(file.tab_info)):
            if file.tab_info[i][2].get() == 1:
                trigger_channels.append(str(i + 1))
                descriptions.append(file.tab_info[i][3].get())

        return trigger_channels, descriptions

    def check_bids_ready(self):
        """
        Check to see whether all contained files required to produce a
        bids-compatible file system have all the necessary data
        """

        # this should be re-written to check only whether the file.is_good
        # property is True to get a nice speed increase.
        # The tag setting is already pretty much handled
        # by the file objects themselves

        if self.is_valid:
            # check the info provided
            is_good = True
            if (self.task_name.get() == '' or
                    self.proj_name.get() == '' or
                    self.subject_ID.get() == ''):
                is_good = False
            if is_good is True:
                # check the contained files.
                # We only need to do this if the info for the project is there
                for _, files in self.contained_files.items():
                    for file in files:
                        if file.is_good is False:
                            is_good = False
                            break
            if is_good is False:
                self.parent.info_notebook.raw_gen_btn.config(
                    {"state": DISABLED})
                self.parent.info_notebook.session_tab.raw_gen_btn.config(
                    {"state": DISABLED})
            else:
                self.parent.info_notebook.raw_gen_btn.config({"state": ACTIVE})
                self.parent.info_notebook.session_tab.raw_gen_btn.config(
                    {"state": ACTIVE})
            return is_good
        else:
            self.parent.info_notebook.raw_gen_btn.config({"state": DISABLED})
            self.parent.info_notebook.session_tab.raw_gen_btn.config(
                {"state": DISABLED})
            return False

    def _set_required_inputs(self):
        # we have a number of basic properties that we need:
        # this should maybe be moved??

        """ Project settings """
        try:
            proj_name = self.parent.file_treeview.item(
                self._id)['text'].split('_')[2]
        except IndexError:
            proj_name = ''
        # try find the specific project settings
        for proj_settings in self.proj_settings:
            if proj_settings.get('ProjectID', None) == proj_name:
                self.proj_settings = proj_settings
                break
        else:
            self.proj_settings = dict()
        self.proj_name.set(proj_name)
        self.task_name = StringVar()
        self.session_ID = StringVar()

        """ Subject settings """
        try:
            sub_name = self.parent.file_treeview.item(
                self._id)['text'].split('_')[0]
        except IndexError:
            sub_name = ''
        self.subject_ID = StringVar()
        self.subject_ID.set(sub_name)
        self.subject_age = IntVar()
        self.subject_gender = StringOptsVar(options=['', 'M', 'F', 'O'])
        subject_groups = flatten(self.settings.get('Groups', ['Participant',
                                                              'Control']))
        self.subject_group.options = subject_groups

        """ Other settings """
        self.dewar_position = StringOptsVar(value='supine',
                                            options=["supine", "upright"])

    def _apply_settings(self, *args):
        """
        A function to be called every time the project ID changes
        to allow the settings to be adjusted accordingly to allow for automatic
        updating of any applicable defaults
        """
        # re-assign the settings to themselves by evoking the setter method
        # of self.settings.
        self.settings = self.parent.proj_settings
        print(self.proj_settings)

    def get(self, name):
        print(name)

    @property
    def ID(self):
        return self._id

    @property
    def settings(self):
        return self.proj_settings

    @settings.setter
    def settings(self, value):
        # try find the specific project settings
        for proj_settings in value:
            if proj_settings.get('ProjectID', None) == self.proj_name.get():
                self.proj_settings = proj_settings
                break
        else:
            self.proj_settings = dict()
        groups = flatten(self.settings.get('Groups', ['Participant',
                                                      'Control']))
        self.subject_group.options = groups

    """
    def __getattr__(self, name):
        # Return None if no property is found with the given name
        return self.__dict__.get(name, None)
    """

    def __repr__(self):
        return str(self._id) + ',' + str(self.file_path)
