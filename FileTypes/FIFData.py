from mne.io import read_raw_fif
from mne.io.constants import FIFF
from datetime import datetime
from numpy import ndarray
from tkinter import messagebox, StringVar
from Management import OptionsVar

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
                    bday = list(self.raw.info['subject_info']['birthday'])
                    bday.reverse()
                    for i, num in enumerate(bday):
                        self.subject_age[i].set(num)
                    gender = {0: 'U', 1: 'M', 2: 'F'}.get(
                        self.raw.info['subject_info']['sex'], 0)
                    self.subject_gender.set(gender)
                else:
                    # TODO: raise popup to notify the user that there is no
                    # subject info and that they need to enter it manually
                    self.subject_ID.set('')
                    for i in self.subject_age:
                        i.set('')
                    self.subject_gender.set('U')

                # load just the BIO channel info if there is any
                for ch in self.raw.info['chs']:
                    if ch['kind'] == FIFF.FIFFV_BIO_CH:
                        self.channel_info[ch['scanno']] = {
                            'ch_name': StringVar(value=ch['ch_name']),
                            'ch_type': OptionsVar(
                                value='EOG',
                                options=['EOG', 'ECG', 'EMG'])}

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
        is_valid &= self.run.get() != ''
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

    def prepare(self):
        BIDSContainer.prepare(self)
        ch_name_map = dict()
        ch_type_map = dict()
        # find any changed names or specified types and set them
        for ch_num, ch_data in self.channel_info.items():
            for ch in self.raw.info['chs']:
                if ch['scanno'] == ch_num:
                    ch_name_map[ch['ch_name']] = ch_data['ch_name'].get()
                    ch_type = ch_data['ch_type'].get()
                    ch_type_map[ch_data['ch_name'].get()] = ch_type.lower()
                    break
        # only do some processing if the data has changed
        if ch_name_map != dict():
            self.raw.rename_channels(ch_name_map)
        if ch_type_map != dict():
            self.raw.set_channel_types(ch_type_map)

        # assign the subject data
        try:
            bday = (int(self.subject_age[2].get()),
                    int(self.subject_age[1].get()),
                    int(self.subject_age[0].get()))
        except ValueError:
            bday = None
        sex = self.subject_gender.get()
        # map the sex to the data used by the raw info
        sex = {'U': 0, 'M': 1, 'F': 2}.get(sex, 0)
        if self.raw.info['subject_info'] is None:
            self.raw.info['subject_info'] = dict()
        self.raw.info['subject_info']['birthday'] = bday
        self.raw.info['subject_info']['sex'] = sex

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
        data['chs'] = dict()
        for num, ch_data in self.channel_info.items():
            data['chs'][num] = [ch_data['ch_name'].get(),
                                ch_data['ch_type'].get()]
        return data

    def __setstate__(self, state):
        BIDSContainer.__setstate__(self, state)
        # Why do we not need this one too???
        #BIDSFile.__setstate__(self, state)
        for key in state.get('chs', []):
            self.channel_info[key] = {
                'ch_name': StringVar(value=state['chs'][key][0]),
                'ch_type': OptionsVar(value=state['chs'][key][1],
                                      options=['EOG', 'ECG', 'EMG'])}
