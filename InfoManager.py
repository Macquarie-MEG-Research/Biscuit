from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *

from InfoEntries import InfoEntry, InfoLabel, InfoChoice, InfoList
from InfoContainer import InfoContainer
from FileTypes import FileInfo

class InfoManager(Notebook):
    """
    A class to organise and keep track of all the information in the info frame
    """
    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(InfoManager, self).__init__(self.master, *args, **kwargs)

        # we always want an "Info" tab
        self.info_tab = Frame(self.master)
        self.info_tab.grid(sticky="nsew")
        self.info_tab.grid_propagate(0)
        self.info_tab.grid_columnconfigure(0, weight=1)
        self.info_tab.grid_rowconfigure(0, weight=1)
        self.info_frame = Frame(self.info_tab)
        self.info_frame.grid(sticky="nsew")
        self.info_frame.grid_propagate(0)
        self.add(self.info_tab, text="Info")

        # let's add a tab with a Text widget, just to see how it goes
        self.text_tab = Frame(self.master)
        self.text_tab.grid()
        textentry = Text(self.text_tab)
        textentry.grid(column = 0, row = 0, sticky="nsew")
        self.text_tab.grid_columnconfigure(0, weight=1)
        self.text_tab.grid_rowconfigure(0, weight=1)
        self.add(self.text_tab, text="Text")

        # finally some objects other widgets that we may like to modify externally
        # by defining them here they will be persistent, so we can draw/undraw them.
        self.raw_gen_btn = Button(self.info_frame, text="Initialise Data", command=self._create_raws, state=DISABLED)

        self._data = None
        self.requires_update = True

    def _create_raws(self):
        self._data[0]._create_raws()

    """
    Each tab type will have it's own function to fill it with data
    """

    def _fill_info_tab(self):
        """
        We will have a list of things to always display
        """
        self.info_frame_entries = []

        data = self._data[0]

        # every time we draw this run the check to see
        data.check_bids_ready()

        if data is not None:
            self.info_frame_entries.append(InfoEntry(self.info_frame, data.subject_ID))
            self.info_frame_entries.append(InfoEntry(self.info_frame, data.task_name))
            self.info_frame_entries.append(InfoEntry(self.info_frame, data.session_ID))
            #self.info_frame_entries.append(InfoEntry(self.info_frame, data.run_number))
            #self.info_frame_entries.append(InfoLabel(self.info_frame, data.measurement_time))
            #self.info_frame_entries.append(InfoLabel(self.info_frame, data.measurement_length))
        else:
            if data.is_valid and not data.initialised:
                data.initiate()
                self._fill_info_tab()
            elif not data.is_valid:
                self._display_invalid_folder()

    def _fill_con_tab(self):
        print('hillo')
    

    # I think this function has no use/won't be needed??
    def determine_tabs(self, context):
        """
        Determine which tabs should be visible due to the current context
        context is the currently selected data object type (eg. .con file, folder etc)
        """
        if context == '.con':
            tab = Frame(self.master)
            tab.grid()
            self.add(tab, text=".con")
            self._fill_con_tab()

    def _display_info_tab(self):

        self.info_frame.grid_forget()
        self._clear_tab(self.info_frame)
        for entry in self.info_frame_entries:
            self.add_gridrow(entry)
        # add a button that can be pressed to generate the RAW objects
        self.raw_gen_btn.grid(row=entry.master.grid_size()[1], column=0)
        self.info_frame.grid(sticky="nsew")

    def _display_nothing(self):
        # This will be shown when there is no actual info to be shown
        self._clear_tab(self.info_frame)
        Label(self.info_frame, text="Nothing to show. Please select something in the file viewer to see info").grid()
    
    def _display_invalid_folder(self):
        self._clear_tab(self.info_frame)
        Label(self.info_frame, text="Selected folder is not a BIDS compatible folder").grid()

    def _display_multiple_types(self):
        self._clear_tab(self.info_frame)
        Label(self.info_frame, text="Multiple files selected. To see information select just one file").grid()

    def _display_known_file(self):
        data_obj = self._data[0]
        self.info_frame.grid_forget()
        self._clear_tab(self.info_frame)
        # undraw the tab before filling it
        # print any file information
        if not data_obj.display_raw:
            anything_displayed = False
            if len(data_obj.info) != 0:
                Label(self.info_frame, text="Information").grid(columnspan=2, sticky=W)
                for data in data_obj.info.items():
                    entry = self.generate_gui_element(self.info_frame, data)
                    self.add_gridrow(entry)
                anything_displayed = True
                Separator(self.info_frame).grid(row = self.info_frame.grid_size()[1], columnspan=2, sticky="ew")
            if len(data_obj.required_info) != 0:
                Label(self.info_frame, text="Required attributes").grid(row = self.info_frame.grid_size()[1], columnspan=2, sticky=W)
                for data in data_obj.required_info.items():
                    entry = self.generate_gui_element(self.info_frame, data)
                    # try and set the background of the entry if it needs to be:
                    try:
                        if entry.value.get() in data_obj.bad_values.get(data[0])['values']:
                            entry.value.config({'background':"Red"})
                    except:
                        pass
                    if data[0] in data_obj.bad_values:
                        entry.set_bads_callback(bad_values=data_obj.bad_values.get(data[0])['values'], parent=data_obj)
                    self.add_gridrow(entry)
                anything_displayed = True
                Separator(self.info_frame).grid(row = self.info_frame.grid_size()[1], columnspan=2, sticky="ew")
            if len(data_obj.optional_info) != 0:
                Label(self.info_frame, text="Optional attributes").grid(row = self.info_frame.grid_size()[1], columnspan=2, sticky=W)
                for data in data_obj.optional_info.items():
                    entry = self.generate_gui_element(self.info_frame, data)
                    self.add_gridrow(entry)
                anything_displayed = True
            
            # have a final check to see if anything has actually been shown.
            # If not, show some message...
            if not anything_displayed:
                Label(self.info_frame, text="No info to show about file sorry!").grid(column=0, row=0, sticky=W)
        else:
            # create a Text widget and read in the file
            textentry = ScrolledText(self.info_frame, wrap=WORD)
            textentry.grid(column = 0, row = 0, sticky='nsew')
            with open(data_obj.file, 'r') as file:
                textentry.insert(END, file.read())

        # re-draw the info frame.
        # by hiding the frame while adding all the sub elements we can avoid a jarring draw effect
        self.info_frame.grid(sticky="nsew")
        if data_obj.display_raw:
            self.info_frame.grid_columnconfigure(0, weight=1)
            self.info_frame.grid_rowconfigure(0, weight=1)
        else:
            self.info_frame.grid_columnconfigure(0, weight=1)
            self.info_frame.grid_columnconfigure(1, weight=3)

    def _display_unknown_file(self):
        self._clear_tab(self.info_frame)
        Label(self.info_frame, text="I don't know how to deal with {0} files yet!!".format(self._data[0].dtype)).grid()

    def _clear_tab(self, tab):
        rows, columns = tab.grid_size()
        # we want to refresh all the grid configurations:
        for row in range(rows):
            tab.grid_rowconfigure(row, weight=0)      # default weight = 0
        for column in range(columns):
            tab.grid_columnconfigure(column, weight=0)

        for child in tab.grid_slaves():
            child.grid_forget()

    def add_gridrow(self, entry):
        """
        Add another row to the grid at the end
        We read the current number of rows from the tab which is contained as a property of the entry
        """
        index = entry.master.grid_size()[1]
        entry.label.grid(row=index, column=0, sticky=E)
        entry.value.grid(row=index, column=1, sticky=W)

    def generate_gui_element(self, master, data):
        """
        This will generate and return the appropriate Info Entry depending
        on the data type of the data.

        Inputs:
        master - the parent widget the returned widget will belong to
        data - a key,value pair containing the name of the data, and the data itself (or a Variable object)
        """
        key, value = data
        if data is not None:
            # we need to pretty much check the data type of the value and return the appropriate gui element
            if isinstance(value, list):
                return InfoList(master, (key, value))
            # check for a generic type:
            elif isinstance(value, (str, int, float, tuple)):
                # in this case, simply create a InfoLabel
                return InfoLabel(master, (key, value))
            # check for Tkinter Variable subclasses.
            elif isinstance(value, Variable):
                # the boolean type we will need to do something different for
                # otherwise return an entry:
                if isinstance(value, (IntVar, StringVar, DoubleVar)):
                    return InfoEntry(master, (key, value))
                elif isinstance(value, BooleanVar):
                    return InfoChoice(master, (key, value))
            else:
                print('Error!!', data)
        else:
            # I dunno...
            raise ValueError

    def populate(self):
        if self._data is not None:
            if len(self._data) == 1:
                if isinstance(self._data[0], InfoContainer):
                    self._fill_info_tab()
            # otherwise we don't need to populate anything

    def draw(self):
        if self._data is None:
            self._display_nothing()
        else:
            if len(self._data) == 1:
                if isinstance(self._data[0], InfoContainer):
                    # display the info about a folder
                    if self._data[0].is_valid:
                        self._display_info_tab()
                    else:
                        self._display_invalid_folder()
                elif isinstance(self._data[0], FileInfo):
                    if self._data[0].unknown_type == False:
                        # in this case we are displaying the info about a single file
                        self._display_known_file()
                    else:
                        self._display_unknown_file()
                    
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
            