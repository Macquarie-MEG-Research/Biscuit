from tkinter.ttk import Label, Frame, Combobox
from tkinter import StringVar, Entry

from Biscuit.CustomWidgets import WidgetTable
from Biscuit.Management.CustomVars import OptionsVar


class BIDSSearchFrame(Frame):

    def __init__(self, master, parent=None, *args, **kwargs):
        self.master = master
        self.parent = parent
        super(BIDSSearchFrame, self).__init__(self.master, *args, **kwargs)

        # create some inital variables
        self.obj_var = OptionsVar(options=['Project', 'Subject', 'Session',
                                           'Scan'])
        self.with_text = StringVar(value='with')
        self.token_var = StringVar()
        self.condition_var = OptionsVar(options=['<', '<=', '=', '!=', '!!=',
                                                 '>=', '>'])
        self.value_var = StringVar()

        self._create_widgets()

        # the associated file
        self._file = None

    def _create_widgets(self):
        self.info_label = Label(self, text="Search")
        self.info_label.grid(column=0, row=0, sticky='nw')

        Label(self, text='Search for a...').grid(column=0, row=1, sticky='nw')

        self.search_table = WidgetTable(
            self,
            headings=["", "", "", "", ""],
            pattern=[OptionsVar, None, StringVar, OptionsVar, StringVar],
            widgets_pattern=[Combobox, Label, Entry, Combobox, Entry],
            data_array=[self.obj_var, self.with_text, self.token_var,
                        self.condition_var, self.value_var])
        self.search_table.grid(column=0, row=2, sticky='nsew')

    def set_text(self, text):
        self.info_label.config(text=text)

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
            self._file = other
