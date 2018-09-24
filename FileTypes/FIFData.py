from mne.io import read_raw_fif
from datetime import datetime
from numpy import ndarray

from .BIDSFile import BIDSFile
from .BIDSContainer import BIDSContainer
#from tkinter import StringVar


class FIFData(BIDSContainer, BIDSFile):
    def __init__(self, id_=None, file=None, settings=None, parent=None):
        BIDSContainer.__init__(self, id_, file, settings, parent)
        BIDSFile.__init__(self, id_, file, settings, parent)

    def _create_vars(self):
        BIDSContainer._create_vars(self)
        BIDSFile._create_vars(self)

    def load_data(self):
        self.raw = read_raw_fif(self.file)
        self.info['Channels'] = self.raw.info['nchan']
        rec_date = self.raw.info['meas_date']
        if isinstance(rec_date, ndarray):
            self.info['Measurement date'] = datetime.fromtimestamp(
                rec_date[0]).strftime('%d/%m/%Y')
        else:
            self.info['Measurement date'] = datetime.fromtimestamp(
                rec_date[0]).strftime('%d/%m/%Y')

        # load subject data
        self.subject_ID.set(self.raw.info['subject_info'].get('id', ''))
        bday = [str(i) for i in self.raw.info['subject_info']['birthday']]
        bday.reverse()
        self.subject_age.set(','.join(bday))
        self.subject_gender.set(
            {0: 'U', 1: 'M', 2: 'F'}.get(self.raw.info['subject_info']['sex'],
                                         0))

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
        is_good = self.check_valid()
        is_good &= BIDSContainer.check_bids_ready(self)
        # since FIF data will always have self.hpi = [], we won't call the
        # BIDSFile.check_valid, and instead repeat the code here without the
        # check for the hpi property...
        print(is_good)
        print('hello')
        self.bids_ready = is_good

    def __getstate__(self):
        a = BIDSContainer.__getstate__(self)
        b = BIDSFile.__getstate__(self)
        # just a dummy for now...
        data = a + b

        return data

    def __setstate__(self, state):
        BIDSContainer.__setstate__(self, state)
        BIDSFile.__setstate__(self, state)

        # first intialise all the required variables
        self._create_vars()
