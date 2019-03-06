from mne.io import read_raw_fif
from mne.io.constants import FIFF
from datetime import datetime
from numpy import ndarray
from tkinter import messagebox, StringVar, IntVar
import os.path as path
import re

from Biscuit.Management import OptionsVar
from .BIDSFile import BIDSFile
from .BIDSContainer import BIDSContainer


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
        self.jobs = set([self])
        self.info['Has Active Shielding'] = "False"
        self.hpi = None

        # name of main file part
        self.mainfile_name = None

        self.interesting_events = set()

        self.associated_event_tab = None

        self.has_error = False

    def load_data(self):
        # first, let's make sure that there are no other files in the same
        # folder with the same name but with a number after it to indicate
        # being part of a split file
        fname, _ = path.splitext(self.file)
        # TODO: this is matched for BIDS produced files. (Don't want!)
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
            finally:
                if self.raw is None:
                    self.has_error = True
                    self.requires_save = False
                    self.loaded = True
                    # in this case the reading of the raw file
                    raise IOError
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

                # load any default event info
                if isinstance(self.container.settings, dict):
                    def_event_info = self.container.settings.get(
                        'DefaultTriggers')

                    if def_event_info is not None:
                        for key, value in def_event_info:
                            if key not in self.interesting_events:
                                self.event_info.append(
                                    {'event': IntVar(value=key),
                                     'description': StringVar(value=value)})
                                self.interesting_events.add(key)

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
        is_valid &= self.run.get() != ''
        return is_valid

    # TODO: maybe not have this return two lists??
    def get_event_data(self):
        events = []
        descriptions = []
        for lst in self.event_info:
            events.append(self._process_event(lst['event'].get()))
            descriptions.append(lst['description'].get())
        return events, descriptions


    # TODO: update this for using current mne_bids
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

    def autodetect_emptyroom(self):
        """ Autodetect if there are any other files in the same folder with the
        same recording data. If so, give them the 'has empty room' property if
        this file has 'is empty room' as True.

        """
        if self.loaded:
            er_date = self.info.get('Measurement date', '')
            # first, get all the files in the same folder that have been
            # loaded (and have the same recording date)
            siblings = []
            parent_sid = self.parent.file_treeview.parent(self.ID)
            for sid in self.parent.file_treeview.get_children(parent_sid):
                if sid in self.parent.preloaded_data:
                    if sid != self.ID:
                        # don't add self
                        obj = self.parent.preloaded_data[sid]
                        if isinstance(obj, FIFData):
                            if obj.info.get(
                                    'Measurement date', None) == er_date:
                                if obj.is_empty_room.get():
                                    # we can only have one empty room file.
                                    # Raise an error message
                                    messagebox.showerror(
                                        "Warning",
                                        "You may only select one empty room "
                                        "file at a time within a project "
                                        "folder. Please deselect the other "
                                        "empty room file to continue.")
                                    return False
                                siblings.append(obj)
            if self.is_empty_room.get():
                # now we can set the state
                for obj in siblings:
                    obj.has_empty_room.set(True)
            else:
                for obj in siblings:
                    obj.has_empty_room.set(False)
        return True

    def _apply_settings(self):
        """ Check the current settings and add any new channels from them """
        # apply BIDSContainer settings first (groups and find correct settings)
        BIDSContainer._apply_settings(self)
        default_events = self.container.settings.get('DefaultTriggers')
        curr_events = self.interesting_events.copy()
        if not self.loaded_from_save:
            if default_events is not None:
                for i, desc in default_events:
                    if i not in curr_events:
                        # add the variables to self.event_info
                        self.event_info.append(
                            {'event': IntVar(value=i),
                             'description': StringVar(value=desc)})
                        self.interesting_events.add(i)

    def _process_event(self, evt):
        """ Take the event provided and convert to the format stored
        in the FIF file """
        """
        # TODO: this may need a bunch of work...?
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
        return event_num

    def __getstate__(self):
        data = BIDSContainer.__getstate__(self)
        data.update(BIDSFile.__getstate__(self))
        data['chs'] = dict()
        for num, ch_data in self.channel_info.items():
            data['chs'][num] = [ch_data['ch_name'].get(),
                                ch_data['ch_type'].get()]
        data['evt'] = dict()
        for evt in self.event_info:
            data['evt'][evt['event'].get()] = evt['description'].get()
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
        for key, value in state.get('evt', dict()).items():
            self.event_info.append({'event': IntVar(value=key),
                                    'description': StringVar(value=value)})
            self.interesting_events.add(key)
