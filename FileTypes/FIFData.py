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

        #self._create_vars()

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

    # self.hpi will be [] for this... FIXME:
    def check_bids_ready(self):
        is_good = self.check_valid()
        is_good &= BIDSContainer.check_bids_ready(self)
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
