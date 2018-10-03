from mne.io import read_raw_fif
from datetime import datetime
from numpy import ndarray
from tkinter import messagebox

import os.path as path
import re

from .BIDSFile import BIDSFile
from .BIDSContainer import BIDSContainer
#from tkinter import StringVar


class FIFData(BIDSContainer, BIDSFile):
    def __init__(self, id_=None, file=None, settings=dict(), parent=None):
        BIDSContainer.__init__(self, id_, file, settings, parent)
        BIDSFile.__init__(self, id_, file, settings, parent)

    def _create_vars(self):
        BIDSContainer._create_vars(self)
        BIDSFile._create_vars(self)
        # as the FIF file is only a single file that contains everything it is
        # its own container, and it's own list of jobs
        self.container = self
        self.jobs = [self]
        self.info['Has Active Shielding'] = "False"

        # name of main file part
        self.mainfile_name = None

    def load_data(self):
        # first, let's make sure that there are no other files in the same
        # folder with the same name but with a number after it to indicate
        # being part of a split file
        fname, _ = path.splitext(self.file)
        m = re.compile(".*-[0-9]")
        if re.match(m, fname):
            # the file is part of a larger one.
            orig_name = ''.join(fname.split('-')[:-1])
            self.mainfile_name = orig_name
            self.requires_save = False
        else:
            try:
                self.raw = read_raw_fif(self.file, verbose='ERROR')
            except ValueError as e:
                if 'Internal Active Shielding' in str(e):
                    if not self.loaded_from_save:
                        messagebox.showinfo(
                            "Active Shield Warning",
                            "The selected file contains active shielding "
                            "data.\nIt can be converted but you should "
                            "process the data.")
                    self.raw = read_raw_fif(self.file, verbose='ERROR',
                                            allow_maxshield=True)
                    self.info['Has Active Shielding'] = "True"
            self.info['Channels'] = self.raw.info['nchan']
            rec_date = self.raw.info['meas_date']
            if isinstance(rec_date, ndarray):
                self.info['Measurement date'] = datetime.fromtimestamp(
                    rec_date[0]).strftime('%d/%m/%Y')
            # TODO: check this still works with MNE 0.16?
            else:
                self.info['Measurement date'] = datetime.fromtimestamp(
                    rec_date[0]).strftime('%d/%m/%Y')

            # only pre-fill this if the file hasn't been loaded from a save
            if not self.loaded_from_save:
                # load subject data
                subject_info = self.raw.info['subject_info']
                if subject_info is not None:
                    self.subject_ID.set(
                        self.raw.info['subject_info'].get('id', ''))
                    bday = [str(i) for i in
                            self.raw.info['subject_info']['birthday']]
                    bday.reverse()
                    self.subject_age.set('/'.join(bday))
                    gender = {0: 'U', 1: 'M', 2: 'F'}.get(
                        self.raw.info['subject_info']['sex'], 0)
                    self.subject_gender.set(gender)
                else:
                    # TODO: raise popup to notify the user that there is no subject
                    # info and that they need to enter it manually
                    self.subject_ID.set('')
                    self.subject_age.set('Unknown')
                    self.subject_gender.set('U')

            self.loaded = True

            self.validate()

    def check_valid(self):
        # this will be essentially custom as we need to be careful due to the
        # fact that the list of jobs contains `self`, which could lead to odd
        # behaviour/possibly an infinite loop.
        is_valid = True
        if self.is_empty_room.get():
            return is_valid
        is_valid &= self.proj_name.get() != ''
        is_valid &= self.subject_ID.get() != ''
        is_valid &= self.task.get() != ''
        is_valid &= self.acquisition.get() != ''
        return is_valid

    def check_bids_ready(self):
        BIDSContainer.check_bids_ready(self)

    # TODO: maybe not have this return two lists??
    def get_event_data(self):
        events = []
        descriptions = []
        for lst in self.event_info:
            events.append(self._process_event(lst['event'].get()))
            descriptions.append(lst['description'].get())
        return events, descriptions

    def _process_event(self, evt):
        """ Take the event provided and convert to the format stored
        in the FIF file """
        """
        if isinstance(evt, str):
            if 'STI' in evt.upper():
                # the event is the name of the channel. Extract the channel
                # number
                ch_num = int(evt[3:])
                event_num = 2**(ch_num - 1)
        else:"""
        # the event is the number encoded on the channel (already 2**(n-1))
        event_num = int(evt)
        # FIXME: this initial value is most likely dependent on the # of chans
        return 0x800 + event_num

    def __getstate__(self):
        data = BIDSContainer.__getstate__(self)
        data.update(BIDSFile.__getstate__(self))
        return data

    def __setstate__(self, state):
        BIDSContainer.__setstate__(self, state)
        # Why do we not need this one too???
        #BIDSFile.__setstate__(self, state)
