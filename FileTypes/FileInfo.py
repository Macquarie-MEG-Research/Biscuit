from collections import OrderedDict
from tkinter import (Variable, TclError)
from utils import pickle_var, unpickle_var

from os.path import normpath


class FileInfo():
    """
    A base class to be subclassed from for various file types
    """
    def __init__(self, id_=None, file=None, parent=None, auto_load=True,
                 treeview=None):
        self._id = id_
        self._file = file
        # parent will be either an InfoContainer object, or none if the file
        # doesn't exist within that context
        self.parent = parent
        self.loaded = False
        self._treeview = treeview    # this is the treeview object so the
        #validation method can affect it

        # a number of info objects
        # self.info is data obtained directly from the raw file
        self.info = OrderedDict()
        # optional info is information that the user can enter if wanted
        self.optional_info = []
        # required info is info that *has* to be entered before BIDS conversion
        #  can occur
        self.required_info = []

        # A dictionary for each file to contain a list of values that the
        # optional_info
        # or required_info dictionaries cannot have
        self.bad_values = dict()

        # A boolean to indicate whether the data is any good.
        # This is set by the verification function to allow for faster
        # determination of whether or not the data is good to be converted to
        # bids format
        self._is_good = True

        self._type = None
        self.unknown_type = False
        # Whether or not the data type needs to be saved in the save data
        self.requires_save = True

        # A flag to be set by the child optionally.
        # If true, then the file contents will be read into a Text widget in
        # the info tab
        self.display_raw = False

        # A list to contain any info specific to the tab generated for this
        # file
        self.tab_info = []

        # this preoperty is used to specify whether or not we want the
        # self.get_info function to be called automatically when the
        # object is created.
        # we will have this as true by default, but for some files we may
        # want it false if the load procedure takes a fair amount of time.
        # In this case we will want the info tab to have a button to press to
        # begin the data
        # generation.
        """ Only override if required to be False """
        self._auto_preload_data = auto_load

        if self._auto_preload_data:
            self.load_data()

    @property
    def ID(self):
        return self._id

    @ID.setter
    def ID(self, value):
        self._id = value

    @property
    def file(self):
        return self._file

    @property
    def dtype(self):
        return self._type

    @property
    def auto_preload_data(self):
        return self._auto_preload_data

    @property
    def treeview(self):
        return self._treeview

    @treeview.setter
    def treeview(self, value):
        self._treeview = value
        # set the is_good value to itself, allowing the gui to be updated
        # with any good or bad values (required when instantiating from
        # pickled data)
        self.is_good = self._is_good

    @property
    def is_good(self):
        return self._is_good

    @is_good.setter
    def is_good(self, value):
        """
        Set the value and automatically change the tag on the treeview
        item to be the appropriate colour.
        """
        if self.treeview is not None:
            if value is True:
                self.treeview.remove_tags(self.ID, ['BAD_FILE'])
                self.treeview.add_tags(self.ID, tags=['GOOD_FILE'])
            elif value is False:
                print(self.ID)
                self.treeview.add_tags(self.ID, tags=['BAD_FILE'])
            else:
                raise ValueError
        # If it is none then this class is being instanced from the pickle.load
        # method. This is fine and later on the self.treeview will be set
        # which will automatically try and re-set the .is_good property,
        # calling this setter again.
        self._is_good = value

    def load_data(self):
        # default method to be overidden by inherited classes
        pass

    # this will probbaly be removed at some point in favor of file specific
    # versions.
    # Maybe leave a basic version. It will depend on whether we decide to add
    # the variables to list like self.required_info (but differently to how
    # they are now...)
    def check_complete(self):
        """
        Function to check whether or not all the required information has been
        entered. If the file has all the required information then return an
        empty list (no bad values).
        Otherwise return the list of keys that require completing
        """
        bads = []
        for key in self.bad_values:
            data = getattr(self, key, None)
            if data is not None:
                if isinstance(data, Variable):
                    # handle the Variable style objects differently as we need
                    # to call .get() on them
                    try:
                        if data.get() in self.bad_values[key]:
                            bads.append((key, data.get()))
                    except TclError:
                        # getting an invalid value. Add to bads
                        bads.append((key, ''))
                else:
                    if data in self.bad_values[key]:
                        bads.append((key, data))
        # if the file has bads, set the tag of the item as bad
        #print(self.bad_values, 'badvals', bads)
        if bads != []:
            print('bad bad!!')
            self.is_good = False
        else:
            self.is_good = True
        return

    def copy(self, new_id):
        """
        This can be called to create another version of the object.
        This will be used when we create the BIDS folder so that the copied
        files already have all the info they need.
        Creating it as a method like this instead of a __copy__ so that we can
        create a copy with a different id
        """
        obj = type(self)(new_id, self._file, parent=self.parent,
                         auto_load=self.auto_preload_data)
        obj.info = self.info
        obj.required_info = self.required_info
        obj.optional_info = self.optional_info
        obj._type = self._type
        obj.unknown_type = self.unknown_type
        return obj

    def __getstate__(self):
        """
        Return the current state of the file and any relevant information
        We do not necessarily want to return all data, as certain value will
        change across loads (such as id)
        """
        data = dict()
        data['file'] = self.file

        def read_data(data):
            output = dict()
            for key, value in data.items():
                # first, let's have a keys that will have specific behaviour:
                if key == 'associated_mrks':
                    # in this case we are trying to serialise a mrk_file object
                    output[key] = [mrk.file for mrk in value['data']]
                else:
                    if isinstance(value, dict):
                        if isinstance(value.get('data', None), Variable):
                            output[key] = pickle_var(value['data'])
                        else:
                            output[key] = value.get('data', None)
                    else:
                        output[key] = value
            return output
        data['info'] = read_data(self.info)     # shouldn't need to save...
        data['optional_info'] = read_data(self.optional_info)
        data['required_info'] = read_data(self.required_info)
        data['tab_info'] = dict()

        print(data)

        return data

    def __setstate__(self, state):
        """
        Take the state supplied and give all the required properties their
        values
        """
        # we simply initialise the class without passing any args so that it
        # can be initialised
        self.__init__(file=state['file'], auto_load=False)
        # the id and parent will be given to it at a later time as they need
        # to be provided by the gui

        def load_data(data, base_data):
            """
            modify base_data in place with the information in 'data'
            """
            for key, value in data.items():
                # handle some specific cases first
                if key == 'associated_mrks':
                    # just set as path for now. We need to replace this with
                    # the actual mrk_file objects but we can't do this until
                    # the mrk files have actually be unpickled.
                    base_data[key] = {'data': value}
                else:
                    # we are going to need to make tuples a restricted data
                    # type so that this doesn't fail...
                    if isinstance(value, tuple):
                        # maybe add a check anyway...
                        # in this case the first entry will be the type, and
                        # second is the value
                        if isinstance(base_data[key], dict):
                            base_data[key]['data'] = unpickle_var(value)
                        else:
                            base_data[key] = unpickle_var(value)
                    else:
                        base_data[key] = value

        load_data(state['info'], self.info)
        load_data(state['optional_info'], self.optional_info)
        load_data(state['required_info'], self.required_info)
        self.tab_info = {}

    def __repr__(self):
        # represent the object by its path.
        # we will normalise the path to make sure the '/'s and '\'s are the
        # same
        return ("<<Id: " + str(self._id) + "\t" + "Path: " +
                str(normpath(self._file)) + ">>")
