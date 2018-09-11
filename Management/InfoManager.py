from tkinter import *
from tkinter import HIDDEN, NORMAL
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *

from CustomWidgets.InfoEntries import InfoEntry, InfoLabel, InfoCheck, InfoList
from FileTypes import FileInfo, InfoContainer
from InfoTabs import FifFileFrame, SessionInfoFrame, ConFileFrame
from InfoTabs.ChannelInfoFrame_new import ChannelInfoFrame as CIF

from utils import clear_widget

# some global names:
T_CON = 'con_tab'
T_FIF = 'fif_tab'
T_EVENTS = 'events_tab'
T_MISC = 'general_tab'
T_FOLDER = 'session_tab'
T_CHANNELS = 'channels_tab'


class InfoManager(Notebook):
    """
    A class to organise and keep track of all the information in the info frame
    """
    def __init__(self, master, parent, context, *args, **kwargs):
        self.master = master
        self.parent = parent        # this will be the main GUI object
        super(InfoManager, self).__init__(self.master, *args, **kwargs)

        self._tabs = {}

        self._data = None
        self.requires_update = True
        self.context = context

        # generic info frame
        self.info_tab = Frame(self)
        self.info_tab.grid(sticky="nsew")
        self.info_tab.grid_propagate(0)
        self.info_tab.grid_columnconfigure(0, weight=1)
        self.info_tab.grid_rowconfigure(0, weight=1)
        self.info_frame = Frame(self.info_tab)
        self.info_frame.grid(sticky="nsew")
        self.info_frame.grid_propagate(0)
        self.add(self.info_tab, text="Info")
        self._tabs[T_MISC] = 0

        # Session info tab (for BIDS-compatible folders)
        self.session_tab = SessionInfoFrame(self, self.parent.settings)
        self.add(self.session_tab, text=" Folder Info")
        self._tabs[T_FOLDER] = 1

        # Info tab for .con files
        self.con_info_tab = ConFileFrame(self, self.parent.settings)
        self.add(self.con_info_tab, text="File Info")
        self._tabs[T_CON] = 2

        """
        # let's add a tab with a Text widget, just to see how it goes
        self.text_tab = Frame(self)
        self.text_tab.grid()
        textentry = Text(self.text_tab)
        textentry.grid(column=0, row=0, sticky="nsew")
        self.text_tab.grid_columnconfigure(0, weight=1)
        self.text_tab.grid_rowconfigure(0, weight=1)
        self.add(self.text_tab, text="Text")
        self._tabs['text'] = 1
        """

        # channels tab (will only be for .con files)
        self.channel_tab = CIF(self, self.parent.settings)
        self.add(self.channel_tab, text="Channels")
        #self.channel_tab.grid(sticky="nsew")
        #self.channel_tab.grid_propagate(0)
        self._tabs[T_CHANNELS] = 3

        # fif file tab
        self.fif_info_tab = FifFileFrame(self, self.parent.settings)
        self.add(self.fif_info_tab, text="File Info")
        self._tabs[T_FIF] = 4

    def determine_tabs(self):
        """
        Determine which tabs should be visible due to the current context
        """
        # If a .con file is selected show the channels tab
        if self.context == '.CON':
            self.channel_tab.file = self._data[0]
            self.con_info_tab.file = self._data[0]
            self.tab(self._tabs[T_FOLDER], state=HIDDEN)
            self.tab(self._tabs[T_MISC], state=HIDDEN)
            self.tab(self._tabs[T_FIF], state=HIDDEN)
            self.tab(self._tabs[T_CON], state=NORMAL)
            self.tab(self._tabs[T_CHANNELS], state=NORMAL)
            if self.context.previous == {'.CON'}:
                self.select(self.select())  # keep current selected
            else:
                self.select(self._tabs[T_CON])
        # If a .fif file is selected then show the fif info tab and event tab
        elif self.context == '.FIF':
            self.fif_info_tab.file = self._data[0]
            self.tab(self._tabs[T_FOLDER], state=HIDDEN)
            self.tab(self._tabs[T_MISC], state=HIDDEN)
            self.tab(self._tabs[T_CON], state=HIDDEN)
            self.tab(self._tabs[T_CHANNELS], state=HIDDEN)
            self.tab(self._tabs[T_FIF], state=NORMAL)
            self.select(self._tabs[T_FIF])
        # if it's a folder we want folder session info
        elif self.context == 'FOLDER':
            if self._data[0].is_valid:
                # only update the session info tab if the data is valid
                self.session_tab.file = self._data[0]
                self.tab(self._tabs[T_FOLDER], state=NORMAL)
                self.tab(self._tabs[T_MISC], state=HIDDEN)
                self.select(self._tabs[T_FOLDER])
            else:
                self.draw_misc()
                self.tab(self._tabs[T_MISC], state=NORMAL)
                self.tab(self._tabs[T_FOLDER], state=HIDDEN)
                self.select(self._tabs[T_MISC])
            self.tab(self._tabs[T_CON], state=HIDDEN)
            self.tab(self._tabs[T_CHANNELS], state=HIDDEN)
            self.tab(self._tabs[T_FIF], state=HIDDEN)
            self.channel_tab.is_loaded = False
        else:
            self.draw_misc()
            self.tab(self._tabs[T_MISC], state=NORMAL)
            self.tab(self._tabs[T_CON], state=HIDDEN)
            self.tab(self._tabs[T_CHANNELS], state=HIDDEN)
            self.tab(self._tabs[T_FOLDER], state=HIDDEN)
            self.tab(self._tabs[T_FIF], state=HIDDEN)
            self.channel_tab.is_loaded = False
            self.select(self._tabs[T_MISC])

    def _display_loading(self):
        # Shows a temporary screen indicating that the requested data is being
        # loaded...
        clear_widget(self.info_frame)
        Label(self.info_frame,
              text="Loading information for selected file, please wait").grid()

    def _display_nothing(self):
        # This will be shown when there is no actual info to be shown
        clear_widget(self.info_frame)
        Label(self.info_frame,
              text="Nothing to show. Please select something in the file "
              "viewer to see info").grid()

    def _display_invalid_folder(self):
        clear_widget(self.info_frame)
        Label(self.info_frame,
              text="Selected folder is not a BIDS compatible folder").grid()

    def _display_multiple_types(self):
        clear_widget(self.info_frame)
        Label(self.info_frame,
              text="Multiple files selected. To see information select just "
              "one file").grid()

    # this needs to be removed I think...
    def _display_known_file(self):
        data_obj = self._data[0]
        self.info_frame.grid_forget()
        clear_widget(self.info_frame)
        # undraw the tab before filling it
        # print any file information
        if not data_obj.display_raw:
            anything_displayed = False
            if len(data_obj.info) != 0:
                Label(self.info_frame, text="Information").grid(columnspan=2,
                                                                sticky=W)
                for data in data_obj.info.items():
                    entry = self.generate_gui_element(self.info_frame, data)
                    self.add_gridrow(entry)
                anything_displayed = True
                Separator(self.info_frame).grid(
                    row=self.info_frame.grid_size()[1], columnspan=2,
                    sticky="ew")
            if len(data_obj.required_info) != 0:
                Label(self.info_frame, text="Required attributes").grid(
                    row=self.info_frame.grid_size()[1], columnspan=2, sticky=W)
                for name, data in data_obj.required_info.items():
                    if data.get('validate', False) is True:
                        # this is a reference to the method so that we can bind
                        # it to a callback in the derived widget
                        validate_cmd = data_obj.check_complete
                    else:
                        validate_cmd = None
                    entry = self.generate_gui_element(
                        self.info_frame, (name, data['data']), validate_cmd,
                        bad_values=data_obj.bad_values.get(name, []))
                    # try and set the background of the entry if it needs to be
                    if isinstance(entry, InfoEntry):
                        entry.check_valid()
                    self.add_gridrow(entry)
                anything_displayed = True
                Separator(self.info_frame).grid(
                    row=self.info_frame.grid_size()[1], columnspan=2,
                    sticky="ew")
            if len(data_obj.optional_info) != 0:
                Label(self.info_frame,
                      text="Optional attributes").grid(
                          row=self.info_frame.grid_size()[1], columnspan=2,
                          sticky=W)
                for name, data in data_obj.optional_info.items():
                    if data.get('validate', False) is True:
                        # this is a reference to the method so that we can bind
                        # it to a callback in the derived widget
                        validate_cmd = data_obj.check_complete
                    else:
                        validate_cmd = None
                    entry = self.generate_gui_element(self.info_frame,
                                                      (name, data['data']),
                                                      validate_cmd)
                    self.add_gridrow(entry)
                anything_displayed = True

            # have a final check to see if anything has actually been shown.
            # If not, show some message...
            if not anything_displayed:
                Label(self.info_frame,
                      text="No info to show about file sorry!").grid(sticky=W)
        else:
            # create a Text widget and read in the file
            textentry = ScrolledText(self.info_frame, wrap=WORD)
            textentry.grid(column=0, row=0, sticky='nsew')
            with open(data_obj.file, 'r') as file:
                textentry.insert(END, file.read())

        # re-draw the info frame.
        # by hiding the frame while adding all the sub elements we can avoid a
        # jarring draw effect
        self.info_frame.grid(sticky="nsew")
        if data_obj.display_raw:
            self.info_frame.grid_columnconfigure(0, weight=1)
            self.info_frame.grid_columnconfigure(1, weight=0)
            self.info_frame.grid_rowconfigure(0, weight=1)
        else:
            self.info_frame.grid_columnconfigure(0, weight=1)
            self.info_frame.grid_columnconfigure(1, weight=3)

    def _display_unknown_file(self):
        clear_widget(self.info_frame)
        Label(self.info_frame,
              text="I don't know how to deal with "
              "{0} files yet!!".format(self._data[0].dtype)).grid()

    def add_gridrow(self, entry):
        """
        Add another row to the grid at the end
        We read the current number of rows from the tab which is contained as a
        property of the entry
        """
        index = entry.master.grid_size()[1]
        entry.label.grid(row=index, column=0, sticky=E)
        entry.value.grid(row=index, column=1, sticky=W)

    def generate_gui_element(self, master, data, validate_cmd=None,
                             bad_values=[]):
        """
        This will generate and return the appropriate Info Entry depending
        on the data type of the data.

        Inputs:
        master - the parent widget the returned widget will belong to
        data - a key,value pair containing the name of the data, and the data
            itself (or a Variable object)
        validate_cmd - The command used for validation of the contents
        """
        key, value = data
        if data is not None:
            # we need to pretty much check the data type of the value and
            # return the appropriate gui element
            if isinstance(value, list):
                return InfoList(master, (key, value), validate_cmd)
            # check for a generic type:
            elif isinstance(value, (str, int, float, tuple)):
                # in this case, simply create a InfoLabel
                return InfoLabel(master, (key, value), validate_cmd)
            # check for Tkinter Variable subclasses.
            elif isinstance(value, Variable):
                # the boolean type we will need to do something different for
                # otherwise return an entry:
                if isinstance(value, (IntVar, StringVar, DoubleVar)):
                    return InfoEntry(master, (key, value), validate_cmd,
                                     bad_values)
                elif isinstance(value, BooleanVar):
                    return InfoCheck(master, (key, value), validate_cmd)
            else:
                print('Error!!', data)
        else:
            # I dunno...
            raise ValueError

    def draw_misc(self):
        if self._data is None:
            self._display_nothing()
        else:
            if len(self._data) == 1:
                if isinstance(self._data[0], InfoContainer):
                    self._display_invalid_folder()
                elif isinstance(self._data[0], FileInfo):
                    if (self._data[0].unknown_type is False and
                            self._data[0].dtype != '.con'):
                        # in this case we are displaying the info about a
                        # single file
                        self._display_known_file()
                    else:
                        self._display_unknown_file()
            elif len(self._data) == 0:
                self._display_nothing()
            else:
                self._display_multiple_types()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        if new_data != self._data:
            self._data = new_data
            self.requires_update = True
        else:
            self.requires_update = False

    def check_context(self):
        # see whether or not the context has changed
        if self.context.changed:
            self.requires_update = True
        else:
            self.requires_update = False

    """
    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, ctx):
        if ctx != self.context:
            self._context = ctx
            self.requires_update = True
        else:
            self.requires_update = False
    """
