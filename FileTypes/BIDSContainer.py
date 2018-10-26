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
    """
    The base object which contains BIDSFiles.
    For KIT data this is the folder that contains the .con, .mrk etc files.
    For Elekta data this is the .fif file itself, so the file is a
    BIDSContainer and a BIDSFile simultanously.
    """
    def __init__(self, id_=None, file=None, settings=None, parent=None):
        super(BIDSContainer, self).__init__(id_, file, parent)

        self._settings = settings

    def _create_vars(self):
        FileInfo._create_vars(self)
        self.proj_name = StringVar()
        self.proj_name.trace("w", self.check_projname_change)
        self.session_ID = StringVar()
        self.session_ID.trace("w", self.validate)
        # this will be a list of BIDSFile's which have their data extracted
        # and passed to mne_bids.
        self.jobs = []

        # subject info
        self.subject_ID = StringVar()
        self.subject_ID.trace("w", self.validate)
        # self.subject_age format [DD, MM, YYYY]
        self.subject_age = [StringVar(), StringVar(), StringVar()]
        self.subject_gender = OptionsVar(options=['M', 'F', 'U'])
        self.subject_group = OptionsVar()
        self.subject_group.trace("w", self._update_groups)

        self.contains_required_files = True
        self.requires_save = True

        self.extra_data = dict()

        # MEG data parameters
        self.electrode = None
        self.hsp = None
        self.readme = None

        self.make_specific_data = dict()

        # whether the object has had any validation done yet
        # This will be used to optimise the validation process since once the
        # BIDSContainer has had it's initial validation checks done, we will
        # only need to check the job for their validation sate, instead of
        # running validation on them again.
        self.validation_initialised = False

    def load_data(self):
        """ do all the intial data loading and variable assignment """
        pass

    def init_validation(self):
        """ Checks the validity of any associated jobs and self"""
        for job in self.jobs:
            job.validate()
        self.validate()
        self.validation_initialised = True

    def validate(self, *args):
        self.valid = self.check_valid()
        self._set_bids_button_state()

    def check_valid(self):
        is_valid = super(BIDSContainer, self).check_valid()
        is_valid &= self.proj_name.get() != ''
        is_valid &= self.subject_ID.get() != ''
        for job in self.jobs:
            is_valid &= job.valid
        return is_valid

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
        self.validate()

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
            if self.valid:
                self.associated_tab.bids_gen_btn.config({"state": ACTIVE})
            else:
                self.associated_tab.bids_gen_btn.config({"state": DISABLED})

    def prepare(self):
        """Prepare all the data in the object to be ready for bids export"""
        # generate the readme
        if isinstance(self.settings, dict):
            self.readme = generate_readme(self.settings)

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value
        self._apply_settings()

    def __getstate__(self):
        # only returns a dictionary of information that we actually need
        # to store.
        data = super(BIDSContainer, self).__getstate__()
        data['prj'] = self.proj_name.get()
        data['sid'] = self.session_ID.get()
        data['sji'] = self.subject_ID.get()
        data['sja'] = [self.subject_age[0].get(),
                       self.subject_age[1].get(),
                       self.subject_age[2].get()]
        data['sjs'] = self.subject_gender.get()
        data['sjg'] = self.subject_group.get()

        return data

    def __setstate__(self, state):
        super(BIDSContainer, self).__setstate__(state)
        self.proj_name.set(state.get('prj', ''))
        self.session_ID.set(state.get('sid', ''))
        self.subject_ID.set(state.get('sji', ''))
        self.subject_age[0].set(state.get('sja', ['', '', ''])[0])
        self.subject_age[1].set(state.get('sja', ['', '', ''])[1])
        self.subject_age[2].set(state.get('sja', ['', '', ''])[2])
        self.subject_gender.set(state.get('sjs', 'M'))
        self.subject_group.set(state.get('sjg', ''))        # TODO: make None?
