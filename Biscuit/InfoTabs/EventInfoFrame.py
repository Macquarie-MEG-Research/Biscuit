from tkinter import StringVar, IntVar, Entry
from tkinter.ttk import Frame
from Biscuit.FileTypes import FIFData
from Biscuit.CustomWidgets.InfoEntries import ValidatedEntry
from Biscuit.CustomWidgets import WidgetTable


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
            remove_script=self._remove_event,
            widgets_pattern=[lambda x: ValidatedEntry(x, force_dtype='int'),
                             Entry],
            sort_column=0)
        self.events_table.grid(sticky='nsew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def _remove_event(self, idx):
        """ Remove the specified index """
        rem_id = self.events_table.data[idx][0].get()
        self.file.interesting_events.remove(rem_id)
        for event in self.file.event_info:
            if event['event'].get() == rem_id:
                self.file.event_info.remove(event)
                break

    def _add_event(self):
        """ Add the two new variables to the underlying FIFData object """
        num = IntVar()
        num.set(0)
        desc = StringVar()
        # set the dictionary key as the name of the variable so that it is
        # unique. We cannot use the actual value here as it will change.
        self.file.event_info.append({'event': num, 'description': desc})
        return [num, desc]

    def update(self):
        data = []
        for d in self.file.event_info:
            data.append([d['event'], d['description']])
        self.events_table.set(data)

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
                if self.file is not None:
                    self._file.associated_event_tab = None
                self._file = other
                self.file.associated_event_tab = self
                self.update()
            else:
                self.is_loaded = False
