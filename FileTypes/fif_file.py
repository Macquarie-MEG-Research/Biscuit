from mne.io import read_raw_fif
from datetime import datetime
from tkinter import BooleanVar, StringVar
from numpy import ndarray

from .FileInfo import FileInfo
from Management import OptionsVar
from utils import flatten, threaded


class fif_file(FileInfo):
    """
    .fif specific file container.
    """
    def __init__(self, id_=None, file=None, *args, **kwargs):
        super(fif_file, self).__init__(id_, file, *args, **kwargs)
        self._type = '.fif'
        self.display_raw = False
        self.requires_save = False

        self.create_vars()

        self.bids_conversion_progress = StringVar()

        if 'emptyroom' in self.file:
            self.is_empty_room.set(True)

    def create_vars(self):
        """
        Create the required Variables
        """
        self.is_junk = BooleanVar()
        self.is_empty_room = BooleanVar()
        self.has_empty_room = BooleanVar()
        self.acquisition = StringVar()
        self.task = StringVar()

        # set any particular bad values
        # The keys of this dictionary must match the keys in the required info
        self.bad_values = {'acquisition': ['']}

        self.proj_name = StringVar()
        self.proj_name.trace("w", self._apply_settings_old)

        # subject info
        self.subject_ID = StringVar()
        self.subject_age = StringVar()  # need to think about this a bit...
        self.subject_gender = OptionsVar(options=['M', 'F', 'U'])
        self.subject_group = OptionsVar()
        self.subject_group.trace("w", self._update_groups)

        self.event_info = {}

    def load_data(self):
        _raw = read_raw_fif(self.file)
        self.info['Channels'] = _raw.info['nchan']
        rec_date = _raw.info['meas_date']
        if isinstance(rec_date, ndarray):
            self.info['Measurement date'] = datetime.fromtimestamp(
                rec_date[0]).strftime('%d/%m/%Y')
        else:
            self.info['Measurement date'] = datetime.fromtimestamp(
                rec_date[0]).strftime('%d/%m/%Y')

        # load subject data
        self.subject_ID.set(_raw.info['subject_info'].get('id', ''))
        bday = [str(i) for i in _raw.info['subject_info']['birthday']]
        bday.reverse()
        self.subject_age.set(','.join(bday))
        self.subject_gender.set(
            {0: 'U', 1: 'M', 2: 'F'}.get(_raw.info['subject_info']['sex'], 0))

        self.loaded = True

    def check_complete(self):
        self.is_good = True

    def check_bids_ready(self):
        return True

    def _apply_settings_old(self, *args):
        """
        A function to be called every time the project ID changes
        to allow the settings to be adjusted accordingly to allow for automatic
        updating of any applicable defaults
        """
        # re-assign the settings to themselves by evoking the setter method
        # of self.settings.
        if self.parent is not None:
            self.settings = self.parent.proj_settings

    def _update_groups(self, *args):
        """Update the EntryChoice that contains the group options"""
        if self.associated_tab is not None:
            self.associated_tab.sub_group_entry.value = self.subject_group

    def _folder_to_bids(self):
        self.parent.check_progress(self.bids_conversion_progress)
        self._make_bids_folders()

    @threaded
    def _make_bids_folders(self):
        pass

    def _apply_settings(self):
        # try find the specific project settings
        if isinstance(self.settings, list):
            for proj_settings in self.settings:
                if (proj_settings.get('ProjectID', None) ==
                        self.proj_name.get()):
                    self._settings = proj_settings
                    break
            else:
                self._settings = dict()
        # otherwise we already have the dictionary of settings correctly
        groups = flatten(self.settings.get('Groups', ['Participant',
                                                      'Control']))
        self.subject_group.options = groups

    def __getstate__(self):
        data = super(fif_file, self).__getstate__()

        return data

    def __setstate__(self, state):
        super(fif_file, self).__setstate__(state)

        # first intialise all the required variables
        self.create_vars()
