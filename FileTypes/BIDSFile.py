from .FileInfo import FileInfo
from tkinter import StringVar, BooleanVar


class BIDSFile(FileInfo):
    def __init__(self, id_=None, file=None, settings=dict(), parent=None):
        super(BIDSFile, self).__init__(id_, file, parent)

        self._settings = settings

        self._create_vars()

        if 'emptyroom' in self.file:
            self.is_empty_room.set(True)

    def _create_vars(self):
        FileInfo._create_vars(self)
        self.acquisition = StringVar()
        self.task = StringVar()
        self.is_junk = BooleanVar()
        self.is_empty_room = BooleanVar()
        self.has_empty_room = BooleanVar()

        self.hpi = []

        self.loaded = False

        self.raw = None
        self.container = None

        # A boolean to indicate whether the data is any good.
        # This is set by the verification function to allow for faster
        # determination of whether or not the data is good to be converted to
        # bids format
        self._is_good = True

    def load_data(self):
        pass

    def validate(self):
        super(BIDSFile, self).validate()

    def update_treeview(self):
        super(BIDSFile, self).update_treeview()

    def check_valid(self):
        """
        Go over all the required settings and determine whether the file is
        ready to be exported to the bids format
        """
        is_good = True
        # if empty room or junk we consider them good
        if self.is_empty_room.get() or self.is_junk.get():
            return is_good
        is_good &= self.task.get() != ''
        is_good &= self.acquisition.get() != ''
        is_good &= (self.hpi != [])
        return is_good

    @property
    def is_good(self):
        return self._is_good

    @is_good.setter
    def is_good(self, value):
        """
        Set the value and call the container's check_bids_ready method
        """
        self._is_good = value
        if self.container is not None:
            self.container.check_bids_ready()

    def __getstate__(self):
        data = super(BIDSFile, self).__getstate__()

        data['acq'] = self.acquisition.get()        # acquisition
        data['tsk'] = self.task.get()               # task
        for hpi in self.hpi:
            data['hpi'].append(hpi)                 # marker coils
        data['jnk'] = self.is_junk.get()            # is junk?
        data['ier'] = self.is_empty_room.get()      # is empty room data?
        data['her'] = self.has_empty_room.get()     # has empty room data?

        return data

    def __setstate__(self, state):
        super(BIDSFile, self).__setstate__(state)

        self.acquisition.set(state['acq'])
        self.task.set(state['tsk'])
        for hpi in state['hpi']:
            self.hpi.append(hpi)
        self.is_junk.set(state['jnk'])
        self.is_empty_room.set(state['ier'])
        self.has_empty_room.set(state['her'])
