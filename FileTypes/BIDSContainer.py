"""
A class which will be inherited by anything that requires the functionality
to be converted to bids data.
This class shouldn't ever be instantiated directly, only to be used as a base
class or tested for with `issubclass`.
"""

from tkinter import StringVar, ACTIVE, DISABLED
from Management import OptionsVar
from .FileInfo import FileInfo
from utils import flatten, generate_readme


class BIDSContainer(FileInfo):
    def __init__(self, id_, file, settings=None, parent=None):
        """
        Parameters:
        id_ - The id of the entry in the treeview
        file - filepath of the folder/file
        settings - settings dictionary from the main gui (to set defaults etc)
        """
        super(BIDSContainer, self).__init__(id_, file, parent)

        self._settings = settings

    def _create_vars(self):
        FileInfo._create_vars(self)
        self.proj_name = StringVar()
        self.proj_name.trace("w", self.check_projname_change)
        self.session_ID = StringVar()
        # this will be a list of BIDSFile's which have their data extracted
        # and passed to mne_bids.
        self.jobs = []

        # subject info
        self.subject_ID = StringVar()
        self.subject_age = StringVar()  # need to think about this a bit...
        self.subject_gender = OptionsVar(options=['M', 'F', 'U'])
        self.subject_group = OptionsVar()
        self.subject_group.trace("w", self._update_groups)

        self.bids_conversion_progress = StringVar()

        self._bids_ready = False

        # MEG data parameters
        self.electrode = None
        self.hsp = None
        self.emptyroom = False
        self.readme = None
        self.extra_data = dict()

        self.event_info = dict()

    def load_data(self):
        """ do all the intial data loading and variable assignment """
        pass

    def check_valid(self):
        print('checking!!')
        is_valid = super(BIDSContainer, self).check_valid()
        is_valid &= self.bids_ready
        return is_valid

    def validate(self):
        super(BIDSContainer, self).validate()

    def update_treeview(self):
        super(BIDSContainer, self).update_treeview()

    def check_bids_ready(self):
        """
        Go over all the required settings and determine whether the file is
        ready to be exported to the bids format
        """
        is_good = True
        is_good &= self.proj_name.get() != ''
        is_good &= self.subject_ID.get() != ''
        for job in self.jobs:
            is_good &= job.is_good
        return is_good

    def check_projname_change(self, *args):
        """
        A function to be called every time the project ID changes
        to allow the settings to be adjusted accordingly to allow for automatic
        updating of any applicable defaults
        """
        # re-assign the settings to themselves by evoking the setter method
        # of self.settings.
        if self.parent is not None:
            self.settings = self.parent.proj_settings
        # not sure if having this here is doubling up and could cause problems
        self.check_bids_ready()

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

    def _update_groups(self, *args):
        """Update the EntryChoice that contains the group options"""
        if self.associated_tab is not None:
            self.associated_tab.sub_group_entry.value = self.subject_group

    def _set_bids_button_state(self):
        """
        Set the state of the button depending on whether it should be
        active or not
        """
        if self.associated_tab is not None:
            if self.bids_ready:
                self.associated_tab.bids_gen_btn.config({"state": ACTIVE})
            else:
                self.associated_tab.bids_gen_btn.config({"state": DISABLED})

    def prepare(self):
        """Prepare all the data in the object to be ready for bids export"""
        # generate the readme
        if isinstance(self.settings, dict):
            self.readme = generate_readme(self.settings)

    @property
    def bids_ready(self):
        return self._bids_ready

    @bids_ready.setter
    def bids_ready(self, value):
        if value != self.bids_ready:
            self._bids_ready = value
            self._set_bids_button_state()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value
        self._apply_settings()

    def __getstate__(self):
        pass

    def __setstate__(self, state):
        pass
