from tkinter.ttk import Label, Frame, Combobox, Button
from tkinter import StringVar, Entry, DISABLED
from webbrowser import open_new as open_hyperlink

from Biscuit.CustomWidgets import WidgetTable
from Biscuit.Management.CustomVars import OptionsVar

HELP_LINK = "https://github.com/Macquarie-MEG-Research/BIDSHandler/blob/master/README.md#querying-bids-data"  # noqa


class BIDSSearchFrame(Frame):

    def __init__(self, master, parent=None, *args, **kwargs):
        self.master = master
        self.parent = parent
        super(BIDSSearchFrame, self).__init__(self.master, *args, **kwargs)

        # create some inital variables
        self.obj_var = OptionsVar(options=['project', 'subject', 'session',
                                           'scan'])
        self.condition_var = OptionsVar(options=['<', '<=', '=', '!=', '!!=',
                                                 '>=', '>'])

        self._create_widgets()

        # the associated file
        self._file = None

    def _create_widgets(self):
        self.info_label = Label(self, text='Search')
        self.info_label.grid(column=0, row=0, sticky='nw')

        Label(self, text='Search for a...').grid(column=0, row=1, sticky='nw')

        self.search_table = WidgetTable(
            self,
            headings=None,
            pattern=[{'var': self.obj_var, 'configs': {'state': 'readonly'}},
                     {'text': 'with'},
                     StringVar,
                     {'var': self.condition_var,
                      'configs': {'state': 'readonly'}},
                     StringVar],
            widgets_pattern=[Combobox, Label, Entry, Combobox, Entry],
            data_array=[
                {'var': self.obj_var, 'configs': {'state': 'readonly'}},
                {'text': 'with'},
                StringVar(),
                {'var': self.condition_var,
                 'configs': {'state': 'readonly'}},
                StringVar()],
            style={'nodividers': True})
        self.search_table.grid(column=0, row=2, columnspan=2, sticky='nsew')

        self.search_button = Button(self, text='Search', command=self.search)
        self.search_button.grid(column=0, row=3, sticky='e')
        help_button = Button(self, text='Help', command=self._open_help)
        help_button.grid(column=1, row=3, sticky='e')

        # results section
        Label(self, text='Results:').grid(column=0, row=4, sticky='nw')
        self.results_frame = WidgetTable(
            self,
            headings=None,
            pattern=[StringVar],
            widgets_pattern=[Label],
            adder_script=DISABLED,
            remove_script=DISABLED,
            max_rows=4)
        self.results_frame.grid(column=0, row=5, columnspan=2, sticky='nsew')

    def search(self):
        query = self.search_table.get()
        results = None
        for q in query:
            if results is None:
                results = self.file.query(q[0], q[2], q[3], q[4])
            else:
                results = results.query(q[0], q[2], q[3], q[4])
        str_results = list([repr(x)] for x in results)
        self.results_frame.set(str_results)

    def _open_help(self):
        open_hyperlink(HELP_LINK)

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
        if other != self._file:
            self._file = other
