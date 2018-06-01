from collections import OrderedDict
from InfoEntries import *
from tkinter import StringVar, IntVar, DoubleVar, BooleanVar, Variable

from os.path import normpath

class FileInfo():
    """
    A base class to be subclassed from for various file types
    """
    def __init__(self, id_, file, parent=None, auto_load = True):
        self._id = id_
        self._file = file
        # parent will be either an InfoContainer object, or none if the file doesn't exist within that context
        self.parent = parent

        # a number of info objects
        # self.info is data obtained directly from the raw file
        self.info = OrderedDict()
        # optional info is information that the user can enter if wanted
        self.optional_info = OrderedDict()
        # required info is info that *has* to be entered before BIDS conversion can occur
        self.required_info = OrderedDict()

        # A dictionary for each file to contain a list of values that the optional_info
        # or required_info dictionaries cannot have
        self.bad_values = dict()

        self._type = None
        self.unknown_type = False

        # A flag to be set by the child optionally.
        # If true, then the file contents will be read into a Text widget in the info tab
        self.display_raw = False

        # this preoperty is used to specify whether or not we want the 
        # self.get_info function to be called automatically when the 
        # object is created.
        # we will have this as true by default, but for some files we may
        # want it false if the load procedure takes a reasonable amount of time.
        # In this case we will want the info tab to have a button to press to begin the data
        # generation.
        """ Only override if required to be Fase """
        self._auto_preload_data = auto_load

        if self._auto_preload_data:
            self.load_data()

    @property
    def ID(self):
        return self._id

    @property
    def file(self):
        return self._file

    @property
    def dtype(self):
        return self._type

    @property
    def auto_preload_data(self):
        return self._auto_preload_data

    def load_data(self):
        # default method to be overidden by inherited classes
        print('loading nothing...')
        pass

    def check_complete(self):
        """
        Function to check whether or not all the required information has been entered
        If the file has all the required information then return an empty list (no bad values).
        Otherwise return the list of keys that require completing
        """
        return []

    def copy(self, new_id):
        """
        This can be called to create another version of the object.
        This will be used when we create the BIDS folder so that the copied files already have all the info they need
        """
        pass

    def __repr__(self):
        # represent the object by its path
        # we will normalise the path to make sure the '/'s and '\'s are the same
        return "<<Id: " + str(self._id) + "\t" + "Path: " + str(normpath(self._file)) + ">>"

    def __str__(self):
        return normpath(self._file)