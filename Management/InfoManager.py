from tkinter import HIDDEN, NORMAL
from tkinter.ttk import Notebook

from FileTypes import FileInfo, Folder, FIFData
from InfoTabs import (FifFileFrame, SessionInfoFrame, ConFileFrame,
                      EventInfoFrame, GenericInfoFrame, ScrolledTextInfoFrame,
                      ChannelInfoFrame)
#from InfoTabs.ChannelInfoFrame_new import ChannelInfoFrame as CIF

# some global names:
T_CON = 'con_tab'
T_FIF = 'fif_tab'
T_EVENTS = 'events_tab'
T_MISC = 'general_tab'
T_FOLDER = 'session_tab'
T_CHANNELS = 'channels_tab'
T_SCROLLTEXT = 'scrolltext_tab'


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

        #TODO: just pass parent instead of parent.settings and allow settings
        # to be retreived one step further down?

        # generic info frame
        self.info_tab = GenericInfoFrame(self)
        self.add(self.info_tab, text="Info")
        self._tabs[T_MISC] = 0

        # Session info tab (for BIDS-compatible folders)
        self.session_tab = SessionInfoFrame(self, self.parent.settings,
                                            self.parent)
        self.add(self.session_tab, text=" Folder Info")
        self._tabs[T_FOLDER] = 1

        # Info tab for .con files
        self.con_info_tab = ConFileFrame(self, self.parent.settings)
        self.add(self.con_info_tab, text="File Info")
        self._tabs[T_CON] = 2

        # channels tab (will only be for .con files)
        self.channel_tab = ChannelInfoFrame(self, self.parent.settings)
        self.add(self.channel_tab, text="Channels")
        self._tabs[T_CHANNELS] = 3

        # fif file tab
        self.fif_info_tab = FifFileFrame(self, self.parent.settings,
                                         self.parent)
        self.add(self.fif_info_tab, text="File Info")
        self._tabs[T_FIF] = 4

        # events tab for fif files
        self.fif_event_tab = EventInfoFrame(self, self.parent.settings)
        self.add(self.fif_event_tab, text="Events")
        self._tabs[T_EVENTS] = 5

        # scrolled text tab
        self.scrolltext_tab = ScrolledTextInfoFrame(self)
        self.add(self.scrolltext_tab, text="File contents")
        self._tabs[T_SCROLLTEXT] = 6

    def determine_tabs(self):
        """
        Determine which tabs should be visible due to the current context
        """
        # If a .con file is selected show the channels tab
        if self.context == '.CON':
            self.channel_tab.file = self.data[0]
            self.con_info_tab.file = self.data[0]
            self.display_tabs(T_CON, T_CHANNELS)
            if self.context.previous == {'.CON'}:
                self.select(self.select())  # keep current selected
            else:
                self.select(self._tabs[T_CON])
        # If a .fif file is selected then show the fif info tab and event tab
        elif self.context == '.FIF':
            if self.data[0].mainfile_name is None:
                self.fif_info_tab.file = self.data[0]
                self.fif_event_tab.file = self.data[0]
                self.display_tabs(T_FIF, T_EVENTS)
                if self.context.previous == {'.FIF'} and self.select() != '':
                    self.select(self.select())  # keep current selected
                else:
                    self.select(self._tabs[T_FIF])
            else:
                self.info_tab.file = self.data[0]
                self.display_tabs(T_MISC)
        # if it's a folder we want folder session info
        elif self.context == 'FOLDER':
            if self.data[0].contains_required_files:
                # only update the session info tab if the data is valid
                self.session_tab.file = self.data[0]
                self.display_tabs(T_FOLDER)
                self.select(self._tabs[T_FOLDER])
            else:
                self.display_tabs(T_MISC)
                self.select(self._tabs[T_MISC])
            self.channel_tab.is_loaded = False
        else:
            if self.data is None:
                self.display_tabs(T_MISC)
                self.select(self._tabs[T_MISC])
            else:
                if self.data[0].display_raw:
                    self.scrolltext_tab.file = self._data[0]
                    self.display_tabs(T_SCROLLTEXT)
                    self.select(self._tabs[T_SCROLLTEXT])
                else:
                    self.display_tabs(T_MISC)
                    self.select(self._tabs[T_MISC])
            self.channel_tab.is_loaded = False

    def _display_loading(self):
        # Shows a temporary screen indicating that the requested data is being
        # loaded...
        self.info_tab.set_text(
            "Loading information for selected file, please wait")

    def _display_nothing(self):
        # This will be shown when there is no actual info to be shown
        self.info_tab.set_text(
            "Nothing to show. Please select something in the file "
            "viewer to see info")

    def _display_invalid_folder(self):
        self.info_tab.set_text(
            "Selected folder is not a BIDS compatible folder")

    def _display_multiple_types(self):
        self.info_tab.set_text(
            "Multiple files selected. To see information select just "
            "one file")

    def _display_unknown_file(self):
        self.info_tab.set_text(
            "I don't know how to deal with "
            "{0} files yet!!".format(self.data[0].dtype))

    def _display_fif_part(self):
        self.info_tab.set_text(
            "File part of {0}.fif".format(self.data[0].mainfile_name))

    def _determine_misc_data(self):
        if self.data is None:
            self._display_nothing()
        else:
            if len(self.data) == 1:
                if isinstance(self.data[0], Folder):
                    self._display_invalid_folder()
                elif isinstance(self.data[0], FIFData):
                    self._display_fif_part()
                elif isinstance(self.data[0], FileInfo):
                    if (self.data[0].unknown_type is False and
                            self.data[0].dtype != '.con'):
                        # in this case we are displaying the info about a
                        # single file
                        pass
                    else:
                        self._display_unknown_file()
            elif len(self.data) == 0:
                self._display_nothing()
            else:
                self._display_multiple_types()

    def display_tabs(self, *tabs):
        """
        Display all tabs provided as values.
        Any tabs that are not on this list will be not displayed.
        If the tab is the T_MISC tab we will also automatically
        determine what is to be displayed in this tab
        """
        for t in self._tabs.keys():
            if t in tabs:
                self.tab(self._tabs[t], state=NORMAL)
                if t == T_MISC:
                    self._determine_misc_data()
            else:
                self.tab(self._tabs[t], state=HIDDEN)

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
