from collections import OrderedDict
from tkinter import BooleanVar

from os.path import normpath


class FileInfo():
    """
    A base class to be subclassed from for various file types
    """
    def __init__(self, id_=None, file=None, parent=None):
        self._id = id_
        self._file = file
        # parent is the main GUI object
        self.parent = parent
        self.loaded = False
        self._create_vars()

    def _create_vars(self):
        # self.info is data obtained directly from the raw file
        # This data will not be saved as it can always just be retreived on
        # instantiation
        self.info = OrderedDict()

        # A dictionary for each file to contain a list of values that the
        # optional_info
        # or required_info dictionaries cannot have
        # REMOVE:
        self.bad_values = dict()

        self._type = None
        self.unknown_type = False
        # Whether or not the data type needs to be saved in the save data
        self.requires_save = False

        # A flag to be set by the child optionally.
        # If true, then the file contents will be read into a Text widget in
        # the info tab
        self.display_raw = False

        # A list to contain any info specific to the tab generated for this
        # file
        self.tab_info = []
        # a pointer to the tab object that is displaying the info for this file
        self.associated_tab = None

        self.is_junk = BooleanVar()
        self.is_junk.set(False)

    def check_valid(self):
        """ Returns True (method will be overriden by derived classes) """
        return True

    def validate(self):
        """
        Check whether the file is valid (ie. contains all the required info for
        BIDS exporting)
        """
        self.is_good = self.check_valid()
        self.update_treeview()

    def update_treeview(self):
        """
        Change the colour of the tag in the treeview to reflect the current
        state of the entry
        """
        if self.parent is not None:
            # check for the is_junk tag. If it has it apply the correct tags.
            if self.is_junk.get() is True:
                self.parent.file_treeview.add_tags(self.ID, ['JUNK_FILE'])
            else:
                self.parent.file_treeview.remove_tags(self.ID, ['JUNK_FILE'])
            # next see if good or not and give the correct tags
            if self.is_good:
                self.parent.file_treeview.remove_tags(self.ID, ['BAD_FILE'])
                self.parent.file_treeview.add_tags(self.ID, tags=['GOOD_FILE'])
            else:
                self.parent.file_treeview.add_tags(self.ID, tags=['BAD_FILE'])
                self.parent.file_treeview.remove_tags(self.ID, ['GOOD_FILE'])
        # if there is no parent, then do nothing...

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

    def load_data(self):
        # default method to be overidden by inherited classes
        pass

    # TODO: fix me!!! please!!!
    def copy(self, new_id):
        """
        This can be called to create another version of the object.
        This will be used when we create the BIDS folder so that the copied
        files already have all the info they need.
        Creating it as a method like this instead of a __copy__ so that we can
        create a copy with a different id
        """
        obj = type(self)(new_id, self._file, parent=self.parent)
        obj.info = self.info
        obj._type = self._type
        obj.unknown_type = self.unknown_type
        return obj

    def __getstate__(self):
        """
        Return the current state of the file and any relevant information
        We do not necessarily want to return all data, as certain value will
        change across loads (such as id)
        """

        if not self.requires_save:
            return
        else:
            data = dict()
            data['file'] = self._file
            return data

    def __setstate__(self, state):
        self.__init__(file=state['file'], auto_load=False)

    def __repr__(self):
        # represent the object by its path.
        # we will normalise the path to make sure the '/'s and '\'s are the
        # same
        return ("<<Id: " + str(self._id) + "\t" + "Path: " +
                str(normpath(self._file)) + "\t" + "Type: " +
                str(self.__class__) + ">>")
