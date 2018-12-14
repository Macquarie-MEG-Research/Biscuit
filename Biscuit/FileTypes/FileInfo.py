from tkinter import BooleanVar
from os.path import normpath


class FileInfo():
    """
    A base container class for the various data types to inherit
    """
    def __init__(self, id_=None, file=None, parent=None):
        """
        Parameters
        ----------
        id_ : str
            Id of the corresponding entry in the file treeview in the main GUI
            window.
        file : str
            Absolute path to the file
        parent : instance of main
            Instance of the main GUI window (`main` class in Biscuit.py)
        """
        self._id = id_
        self._file = file
        self.parent = parent
        self.loaded = False
        self._create_vars()

#region public methods

    def check_valid(self):
        """ Returns True (method will be overriden by derived classes) """
        return True

    def load_data(self):
        # default method to be overidden by inherited classes
        pass

    def validate(self, *args):
        """
        Check whether the file is valid (ie. contains all the required info for
        BIDS exporting)
        """
        self.valid = self.check_valid()

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
            if self.valid:
                self.parent.file_treeview.remove_tags(self.ID, ['BAD_FILE'])
                self.parent.file_treeview.add_tags(self.ID, tags=['GOOD_FILE'])
            else:
                self.parent.file_treeview.add_tags(self.ID, tags=['BAD_FILE'])
                self.parent.file_treeview.remove_tags(self.ID, ['GOOD_FILE'])

#region private methods

    def _apply_settings(self):
        pass

    def _create_vars(self):
        """ Create all the required data for the file """
        self.info = dict()

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

        self.is_valid = True

        self.loaded_from_save = False

        # used for files that are viewed with the text viewer
        self.saved_time = "Never"

#region properties

    @property
    def ID(self):
        return self._id

    @ID.setter
    def ID(self, value):
        self._id = value

    @property
    def valid(self):
        return self.is_valid

    @valid.setter
    def valid(self, other):
        self.is_valid = other
        self.update_treeview()

    @property
    def file(self):
        return self._file

    @property
    def dtype(self):
        return self._type

#region class methods

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
            data['jnk'] = self.is_junk.get()
            return data

    def __setstate__(self, state):
        self.__init__(file=state['file'])
        self.is_junk.set(state.get('jnk', False))

    def __repr__(self):
        """
        Represent the object by its path.
        We will normalise the path to make sure the '/'s and '\'s are the
        same
        """
        return ("<<Id: " + str(self._id) + "\t" + "Path: " +
                str(normpath(self._file)) + "\t" + "Type: " +
                str(self.__class__) + ">>")
