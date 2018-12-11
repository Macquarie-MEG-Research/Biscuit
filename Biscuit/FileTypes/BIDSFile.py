from .FileInfo import FileInfo
from Biscuit.Management import OptionsVar
from tkinter import StringVar, BooleanVar


class BIDSFile(FileInfo):
    """
    BIDSFiles are the main files which will contain the data that is to be
    converted to BIDS format.
    For KIT data this is the .con file.
    For Elekta data this is the .fif file.

    """
    def __init__(self, id_=None, file=None, settings=dict(), parent=None):
        super(BIDSFile, self).__init__(id_, file, parent)

        self._settings = settings

        self._create_vars()

        if 'emptyroom' in self.file:
            self.is_empty_room.set(True)

    def _create_vars(self):
        # TODO: Fix
        # This is called multiple times...
        FileInfo._create_vars(self)
        self.run = StringVar(value='1')
        self.run.trace("w", self.validate)
        self.task = OptionsVar(options=['None'])
        self.task.trace("w", self._update_tasks)
        self.is_junk = BooleanVar()
        self.is_empty_room = BooleanVar()
        self.is_empty_room.trace("w", self.propagate_emptyroom_data)
        self.has_empty_room = BooleanVar()

        self.hpi = []

        self.loaded = False

        self.extra_data = dict()

        # event info: a list of lists. The sub-lists contains the event number
        # and the event description
        self.event_info = list()
        # channel info: key - channel name (?), value - something
        self.channel_info = dict()

        self.raw = None
        self.container = None

        # Set all BIDS files to be saved by default
        self.requires_save = True

    def load_data(self):
        pass

    def validate(self, validate_container=True, *args):
        """
        Check whether the file is valid (ie. contains all the required info for
        BIDS exporting).

        """
        self.valid = self.check_valid()
        if self.container is not None and validate_container:
            self.container.validate()

    def check_valid(self):
        """
        Go over all the required settings and determine whether the file is
        ready to be exported to the bids format.

        """
        is_valid = super(BIDSFile, self).check_valid()
        # if empty room or junk we consider them good
        if self.is_empty_room.get() or self.is_junk.get():
            return is_valid
        is_valid &= self.run.get() != ''
        is_valid &= (self.hpi != [])
        return is_valid

    def get_event_data(self):
        return ['', '']

    def propagate_emptyroom_data(self, *args):
        """ Callback to propagate the empty room state

        This is used to tell the container object that the empty room status
        of this file has changed and change the 'has empty room' state of any
        other files in the same folder (for KIT).

        """
        if self.container is not None:
            emptyroom_set = self.container.autodetect_emptyroom()
            if not emptyroom_set:
                self.is_empty_room.set(False)
                self.associated_tab.is_emptyroom_info.value = self.is_empty_room  # noqa

    def _update_tasks(self, *args):
        """Update the EntryChoice that contains the task options"""
        if self.associated_tab is not None:
            self.associated_tab.task_info.value = self.task

    def __getstate__(self):
        data = super(BIDSFile, self).__getstate__()

        data['run'] = self.run.get()        # run
        data['tsk'] = self.task.get()       # task
        if self.hpi is not None:
            data['hpi'] = [hpi.file for hpi in self.hpi]        # marker coils
        else:
            data['hpi'] = None
        data['ier'] = self.is_empty_room.get()      # is empty room data?
        data['her'] = self.has_empty_room.get()     # has empty room data?

        return data

    def __setstate__(self, state):
        super(BIDSFile, self).__setstate__(state)
        self.run.set(state.get('run', 0))
        task = state.get('tsk', '')
        self.task.options = [task]
        self.task.set(task)
        # these will be just the file paths for now
        self.hpi = state.get('hpi', None)
        self.is_empty_room.set(state.get('ier', False))
        self.has_empty_room.set(state.get('her', False))
