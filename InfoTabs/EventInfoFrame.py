from tkinter import Frame, StringVar, IntVar
#from tkinter import Button as tkButton
from tkinter.ttk import Entry
from FileTypes import FIFData
from CustomWidgets.WidgetTable import WidgetTable


class EventInfoFrame(Frame):
    def __init__(self, master, default_settings, *args, **kwargs):
        self.master = master
        self.default_settings = default_settings
        super(EventInfoFrame, self).__init__(self.master, *args, **kwargs)

        self._create_widgets()

        # two lists to keep track of which values are shown and which aren't
        self.channel_name_states = {'not shown': [], 'shown': []}

        # the con file object
        self._file = None
        self.is_loaded = False
        self.channel_widgets = {}

    def _create_widgets(self):
        self.events_table = WidgetTable(
            self,
            headings=["Event number", "Event description"],
            pattern=[IntVar, StringVar],
            adder_script=self._add_event,
            widgets_pattern=[Entry, Entry],
            sort_column=0)
        self.events_table.grid(sticky='nsew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def _add_event(self):
        """ Add the two new variables to the underlying FIFData object """
        num = IntVar()
        desc = StringVar()
        self._file.event_info['num'] = num
        self._file.event_info['description'] = desc
        return [num, desc]

    # FIXME:
    def update(self):
        pass

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, other):
        """
        Set the file property to whatever the new file is.
        When this happens the update command will be called which will redraw
        the channel info list
        """
        # if the file is being set as a con_file continue
        if other != self._file:
            if isinstance(other, FIFData):
                self._file = other
                self.update()
            else:
                self.is_loaded = False
