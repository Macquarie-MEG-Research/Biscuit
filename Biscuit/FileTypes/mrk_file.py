from os.path import basename
from tkinter import StringVar

from .FileInfo import FileInfo
from Biscuit.utils.constants import MRK_NA, MRK_PRE, MRK_POST, MRK_MULT


class mrk_file(FileInfo):
    """
    .mrk specific file container.
    """
    def __init__(self, id_=None, file=None, parent=None):
        super(mrk_file, self).__init__(id_, file, parent)
        self._type = '.mrk'

    def _create_vars(self):
        super(mrk_file, self)._create_vars()

        # we need a variable indicating whether the mrk file was recorded
        # before or after the experiment, or whether it doesn't matter
        self.acquisition = StringVar()
        self.acquisition.set(MRK_NA)
        for acq in [MRK_PRE, MRK_POST, MRK_MULT]:
            if acq in self.file.lower():
                self.acquisition.set(acq)
                break
        self.acquisition.trace("w", self._set_save_state)

    def _set_save_state(self, *args):
        """ Set whether the file needs to be saved by checking if
        self.acquisition != 'n/a' """
        if self.acquisition.get() != MRK_NA:
            self.requires_save = True
        else:
            self.requires_save = False

    def __getstate__(self):
        print(self.requires_save)
        data = super(mrk_file, self).__getstate__()

        data['acq'] = self.acquisition.get()        # acquisition

        return data

    def __setstate__(self, state):
        super(mrk_file, self).__setstate__(state)
        self.acquisition.set(state.get('acq', MRK_NA))

    def __repr__(self):
        # Have a separate representation for .mrk files as this is shown in the
        # info for each con file under the list of associated mrk's.
        return str(basename(self.file))
