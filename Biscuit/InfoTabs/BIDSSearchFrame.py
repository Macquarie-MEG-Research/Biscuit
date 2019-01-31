from tkinter.ttk import Label, Frame, Combobox, Button
from tkinter import StringVar, Entry, Text, Scrollbar
from tkinter import END, FLAT, NORMAL, DISABLED, HORIZONTAL, NONE
from webbrowser import open_new as open_hyperlink
import os.path as op

from bidshandler import Scan

from Biscuit.utils.utils import str_to_obj, get_bidsobj_info
from Biscuit.utils.constants import OSCONST
from Biscuit.CustomWidgets import WidgetTable
from Biscuit.Management.CustomVars import OptionsVar
from Biscuit.Management.tkHyperlinkManager import HyperlinkManager

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

#region public methods

    def set_text(self, text):
        self.info_label.config(text=text)

#region private methods

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

        self.search_button = Button(self, text='Search', command=self._search)
        self.search_button.grid(column=0, row=3, sticky='e')
        help_button = Button(self, text='Help', command=self._open_help)
        help_button.grid(column=1, row=3, sticky='e')

        # results section
        Label(self, text='Results:').grid(column=0, row=4, sticky='nw')

        frame = Frame(self)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        xscrollbar = Scrollbar(frame, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky='ew')

        yscrollbar = Scrollbar(frame)
        yscrollbar.grid(row=0, column=1, sticky='ns')

        self.results_frame = Text(frame, relief=FLAT, undo=False, takefocus=0,
                                  bg=OSCONST.TEXT_BG, wrap=NONE,
                                  xscrollcommand=xscrollbar.set,
                                  yscrollcommand=yscrollbar.set)

        self.results_frame.grid(row=0, column=0, sticky='nsew')

        self.hyperlink = HyperlinkManager(self.results_frame)

        xscrollbar.config(command=self.results_frame.xview)
        yscrollbar.config(command=self.results_frame.yview)

        frame.grid(column=0, row=5, columnspan=2, sticky='nsew')

        self.result_count_label = Label(self, text="Total results: 0")
        self.result_count_label.grid(column=0, row=6, sticky='w')

    def _open_help(self):
        open_hyperlink(HELP_LINK)

    def _search(self):
        query = self.search_table.get()
        results = None
        for q in query:
            if results is None:
                results = self.file.query(q[0], q[2], q[3], str_to_obj(q[4]))
            else:
                results = results.query(q[0], q[2], q[3], str_to_obj(q[4]))
        str_results = list(get_bidsobj_info(x) for x in results)
        self.results_frame.config(state=NORMAL)
        # Clear all the current text.
        self.results_frame.delete(1.0, END)
        # Then add all the new results.
        for i, result in enumerate(str_results):
            self.results_frame.insert(
                END,
                result + '\n',
                self.hyperlink.add(
                    lambda obj=results[i]: self._select_obj(obj)))
        # Set the frame to not be writable any more.
        self.results_frame.config(state=DISABLED)

        self.result_count_label.config(
            text="Total results: {0}".format(len(results)))

    def _select_obj(self, obj):
        """Highlight the selected object in the treeview."""
        # find the selected object's sid
        if isinstance(obj, Scan):
            # for scan objects we want to go to the actual raw object
            fpath = obj.raw_file
        else:
            fpath = obj.path
        obj_sid = self.parent.file_treeview.sid_from_filepath(fpath)
        # then show it
        print(obj_sid)
        self.parent.file_treeview.see(obj_sid)
        self.parent.file_treeview.focus(item=obj_sid)
        self.parent.file_treeview.selection_set((obj_sid,))

#region properties

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
