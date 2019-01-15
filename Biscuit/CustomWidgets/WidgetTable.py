from tkinter import Variable, DISABLED
from tkinter import Button as tkButton
from tkinter import Entry as tkEntry
from tkinter.ttk import (Label, Separator, Button, Frame, Checkbutton,
                         Combobox)
from PIL import Image, ImageTk
# import copy so we can create static copies of the reference functions in the
# underlying pattern of a row if any.
from copy import copy

from Biscuit.utils.constants import OSCONST
from Biscuit.utils.utils import copy_dict

from .ScrollableFrame import ScrollableFrame


class WidgetTable(Frame):
    """
    A frame which contains rows which can be populate with multiple
    widgets in each column.
    We can have a button to remove rows, and a few different ways to add new
    rows.

    Parameters
    ----------
    headings : list(str)
        A list of strings for the headings
    pattern : list(instance of Variable)
        A list of Variables to be associated with the widget.
        These variables need to be the appropriate type for the
        entry_type associated with the data, as well as the data passed in
        (if the table is to be initially or automatically populated).
        The Variable information can be passed in as a dicitonary to allow
        very specific modification of how the data works.
        The dictionary has the following keys:
        - var: An instantiated Variable object
        - text: A string (used as the text on buttons, or default text
            for an entry/label)
        - configs: A dictionary of the configuration to be applied to the
            widget.
        - func: The function used as a callback for buttons, checkbuttons
            etc.
        - func_has_row_ctx: (bool) whether or not the function specified by
            func is given the current line as an argument.
    widgets_pattern : list(instance of Widget)
        A list of Widgets that will be drawn in each
        column.
        These widgets *must* be un-instantiated to allow cloning when
        creating new rows.
    add_options : list
        A fixed length list of options that can be added.
        If None then the rows can just be added arbitrarily using button.
    data_array : list
        A list of the intial data to populate the table with.
        This can either be raw data or an array of the variables
    adder_script : function
        A function that will be called when the Add button is
        pressed or a value is picked from the add_options option box.
        If this function returns an values they are assumed to be the
        values to be passed into the newly created widgets if possible.
    remove_script : function
        A callback for when a row is deleted.
        This function can be used to block deletion. This is acheived by having
        this function return anything. If nothing is returned then the deletion
        occurs as expected.
    sort_column : int
        The column number that the data will automatically be sorted by.
    max_rows : int
        The maximum number of rows to display before forcing the
        ScrollableFrame to have a scroller.

    """
    def __init__(self, master, headings=[], pattern=[], widgets_pattern=[],
                 add_options=None, data_array=[], adder_script=None,
                 remove_script=None, sort_column=None, max_rows=None, *args,
                 **kwargs):
        self.master = master

        # s = Style(self.master)
        # s.configure('proper.TEntry', background='green')

        super(WidgetTable, self).__init__(self.master, *args, **kwargs)

        self.rows = []
        self.headings = headings
        self.pattern = pattern
        self.widgets_pattern = widgets_pattern
        self.num_columns = len(self.headings)
        self.add_options = add_options
        self.adder_script = adder_script
        self.remove_script = remove_script
        self.sort_column = sort_column
        self.max_rows = max_rows

        self.entry_config = {'readonlybackground': OSCONST.TEXT_RONLY_BG,
                             'highlightbackground': OSCONST.TEXT_BG}

        # the index we need to redraw the rows after
        self.first_redraw_row = 0

        self.row_offset = 0
        self.separator_offset = 0

        self.widgets = []
        self.add_button = None
        self._create_widgets()

        self.separators = []
        for _ in range(self.num_columns - 1):
            sep = Separator(self.sf.frame, orient='vertical')
            self.separators.append(sep)

        self.delete_icon = Image.open(OSCONST.ICON_REMOVE)
        self.delete_icon = self.delete_icon.resize((20, 20), Image.LANCZOS)
        self.delete_icon = ImageTk.PhotoImage(self.delete_icon)

        # storage variables
        if data_array != []:
            # ensure a 2D array
            if not isinstance(data_array[0], list):
                data_array = [data_array]
            self.data = []
            self.set(data_array)
        else:
            # empty table
            self.data = []
            self._draw_separators()

        self.bind(OSCONST.ADDROW, self._add_row_from_key)

#region public methods

    def add_row_data(self, idx, data=None):
        """
        Add the provided row data at the required index

        Paramaters
        ----------
        idx : int
            Index the data is the be added at.
        data : list
            This is a list of either the values the variables will take or the
            data itself.
            Any entry can be None which indicates the default un-initiated data
            should be used.

        """
        # TODO: fix the optimisation so that this is not 0 any more...
        self.first_redraw_row = 0  # len(self.data) - 1
        self._assign_row_data(idx, data)

    def add_row_widgets(self, count=1):
        """ Add one or more sets of row widgets to the end of the table
        The widgets are added from the WidgetTable's widget_pattern property.

        Parameters
        ----------
        count : int
            The number of rows of widgets to add.
            Defaults to 1

        """
        # remove the add button if it exists
        if count != 0:
            if self.add_button is not None:
                self.add_button.grid_forget()

            initial_rows = len(self.widgets)

        for r in range(count):
            row_widgets = []

            rows = self.sf.frame.grid_size()[1]
            # draw each of the new widgets in the last row
            for i, w in enumerate(self.widgets_pattern):
                w_actual = w(self.sf.frame)
                w_actual.bind(OSCONST.ADDROW, self._add_row_from_key)
                w_actual.grid(row=rows, column=2 * i, sticky='nsew', padx=2,
                              pady=2)
                row_widgets.append(w_actual)

            # add the delete button at the end of the row
            if self.remove_script != DISABLED:
                curr_row = initial_rows + r
                delete_button = tkButton(
                    self.sf.frame,
                    command=lambda x=curr_row: self.delete_rows_and_update(x),
                    relief='flat', borderwidth=0, highlightthickness=0,
                    takefocus=0)
                delete_button.config(image=self.delete_icon)
                delete_button.grid(row=rows, column=2 * self.num_columns - 1)
                row_widgets.append(delete_button)
            self.widgets.append(row_widgets)

            # set the focus on the first of the widgets in the bottom row
            # TODO: this will probably need a bit more complexity added to it??
            self.widgets[-1][0].focus_set()

        if count != 0:
            # finally, fix up separators and add button if needed
            self._draw_separators()
            if self.add_button is not None:
                self.add_button.grid(row=rows + 1,
                                     column=2 * self.num_columns - 1)

    def add_rows(self, data=None, count=1, from_start=False):
        """
        Add a new row to the end of the current data and redraw all the
        current data from the new data onward.
        We can add multiple rows at a time to save drawing, undrawing then
        drawing the add button again and again.

        Parameters
        data : list | None
            Data to be automatically added to the new row(s)
        count : int
            Number of new rows to add.
            Defaults to 1.
        from_start : bool
            Whether to assign row data from the start of not.
            This should always be False unless count == 0.
        """
        refresh = False

        # if from_start == True then the data will be placed from row 0
        curr_rows = (1 - from_start) * len(self.data)
        # if there is no size difference we simply want to refresh the data
        if count == 0:
            refresh = True
            count = len(data)
        if data is not None and data != []:
            data = self.ensure_2D_array(data)
            for i in range(count):
                self.add_row_data(curr_rows + i, data[i])
        else:
            for i in range(count):
                self.add_row_data(curr_rows + i)

        if not refresh:
            self.add_row_widgets(count)

        # now sort the data if needed.
        # we only want to sort if data is provided, otherwise we can have weird
        # effects like the new data being inserted at the start.
        if data is not None:
            self.sort_data()

        self._correct_idx_refs()

        # apply the data appropriately
        self._apply_data()

    def add_row_from_button(self):
        """ Add a row from the 'Add Row' button """
        # before anything happens call the adder script if there is one to
        # determine whether there is any data that can populate the new row.
        if self.adder_script is not None:
            try:
                ret = self.adder_script()
                if ret is None:
                    self.add_rows()
                else:
                    self.add_rows(ret)
            except TypeError:
                # in this case the wrong number of arguments have been passed
                # (potentially. Print a message and pass)
                print(("The adder function used wasn't called because "
                       "it had the wrong number of arguments"))
            except ValueError:
                # In this case the function may have broken.
                # This indicates we do not want to add the row
                pass
        else:
            self.add_rows()

        self._resize_to_max(move_to_bottom=True)

    def add_row_from_selection(self, event):
        """ Add a new row from the list of possible rows to add """
        # this only needs to be different to implement the functionality to
        # allow the entry in the list to be removed if it needs to be
        # unless we leave that functionality up to the user...
        if self.adder_script is not None:
            ret = self.adder_script()
            if ret is None:
                self.add_rows()
            else:
                self.add_rows(ret)
        self._resize_to_max(resize_canvas='x')

    def delete_row(self, idx, ignore_script=False):
        """ Remove the row widgets and data

        Parameters
        ----------
        idx : int
            Row index to delete.
        ignore_script : bool
            Whether or not to ignore the call to the removal script.
            Defaults to False (runs removal script by default if there is one)

        """
        remove_rtn = None
        if self.remove_script is not None and not ignore_script:
            remove_rtn = self.remove_script(idx)
        if remove_rtn is None:
            for w in self.widgets[-1]:
                w.grid_forget()
            del self.widgets[-1]
            del self.data[idx]

    def delete_rows_and_update(self, idx, count=1, ignore_script=False):
        """ Remove one or more row widgets and update the table

        Parameters
        ----------
        idx : int
            Row index to delete.
        count : int
            Number of rows to delete. Defaults to 1.
        ignore_script : bool
            Whether or not to ignore the call to the removal script.
            Defaults to False (runs removal script by default if there is one).

        """
        # remove up to the maximum number of rows
        for _ in range(min(len(self.widgets), count)):
            self.delete_row(idx, ignore_script)
        # remap the delete command for the buttons
        for i in range(len(self.widgets)):
            del_btn = self.widgets[i][-1]
            del_btn.config(command=lambda x=i: self.delete_rows_and_update(x))
        # now, reapply all the variables
        self.first_redraw_row = 0
        self._correct_idx_refs()
        self._apply_data()
        self.sf.configure_view(resize_canvas='')

    def get(self, values=True):
        """
        Return a 2D array of all the data contained.

        Parameters
        ----------
        values : bool
            If values == True, the value of the Variables will be
        returned. If False the Variables themselves will be returned
        """
        out_data = []
        for row in self.data:
            row_data = []
            if values:
                for var in row:
                    if not isinstance(var, dict):
                        row_data.append(var.get())
                    else:
                        if 'var' in var:
                            row_data.append(var['var'].get())
                        elif 'text' in var:
                            row_data.append(var['text'])
            else:
                # simply return the actual row data
                row_data.append(row)
            out_data.append(row_data)
        return out_data

    def set(self, data=[]):
        """
        Force the table to be updated with new data
        """
        diff = len(data) - len(self.data)
        if diff < 0:
            # assign the row data
            for i in range(len(data)):
                self.add_row_data(i, data[i])
            # remove all unneccesary rows
            self.delete_rows_and_update(-1, abs(diff), ignore_script=True)
        elif diff > 0:
            # assign the data up to the number of existing widgets
            for i in range(len(data) - diff):
                self.add_row_data(i, data[i])
            self.add_rows(data[-diff:], diff)
        elif diff == 0:
            self.add_rows(data, diff, from_start=True)

        self._resize_to_max()

    def set_row(self, idx, data):
        """
        Set the data for a specific row

        Parameters
        ----------
        idx : int
            Index of the row the data will be set in.
        data : list
            Row data to be assigned. This should be a list of raw values, not
            a list of instances of Variables.
        """
        for i, val in enumerate(data):
            if val is not None:
                self.data[idx][i].set(val)

    def sort_data(self):
        """ If a sort column is specified on intialisation of the WidgetTable
        then sort by this column."""
        if isinstance(self.sort_column, int):
            if self.sort_column < self.num_columns:
                self.data.sort(key=lambda x: x[self.sort_column].get())

#region private methods

    def _add_row_from_key(self, *args):
        """ Add a new row when the new row keyboard shortcut is pressed

        This will only be possible when we don't have a fixed list of
        possibilites to add.

        """
        if not isinstance(self.add_options, list):
            self.add_row_from_button()
            self.sf.configure_view(resize_canvas='x')

    def _apply_data(self):
        """
        Apply all the data in self.data to the widget array.
        The widgets are traversed column by column so that we can create an
        apply function specifically for that widget type.
        """
        # do columns then rows to save having to check data types repeatedly
        for column in range(self.num_columns):
            # first, create a lambda which can be re-used for each row
            w = self.widgets_pattern[column]
            try:
                if callable(w):
                    # in this case the widget is actually one wrapped in a
                    # lambda statement.
                    # extract it by checking the type
                    w = type(w(self))
                if issubclass(w, Label):
                    if isinstance(self.pattern[column], dict):
                        # apply any provided configs:
                        apply = lambda wgt, var: wgt.configure(  # noqa: E731
                            textvariable=var['var'],
                            **var.get('configs', dict()))
                    else:
                        apply = lambda wgt, var: wgt.configure(  # noqa: E731
                            textvariable=var)
                if issubclass(w, tkEntry):
                    if isinstance(self.pattern[column], dict):
                        # apply any provided configs:
                        apply = lambda wgt, var: wgt.configure(  # noqa: E731
                            textvariable=var['var'], **self.entry_config,
                            **var.get('configs', dict()))
                    else:
                        apply = lambda wgt, var: wgt.configure(  # noqa: E731
                            textvariable=var, **self.entry_config)
                if issubclass(w, Checkbutton):
                    # check underlying data type to provide correct function
                    if isinstance(self.pattern[column], dict):
                        apply = lambda wgt, var: wgt.configure(  # noqa: E731
                            variable=var['var'], command=var.get('func', None),
                            **var.get('configs', dict()))
                    else:
                        apply = lambda wgt, var: wgt.configure(variable=var)  # noqa: E731,E501
                elif issubclass(w, Button):
                    apply = lambda wgt, var: wgt.configure(text=var['text'],  # noqa: E731,E501
                                                           command=var['func'])
                elif issubclass(w, Combobox):
                    # we will be assuming that the underlying data type is an
                    # OptionsVar to provide simplest functionality
                    def apply(wgt, var):
                        wgt.configure(values=var.options, state='readonly')
                        wgt.set(var.get())
                        # set the selection binding
                        select_value = lambda e, w=wgt: var.set(wgt.get())  # noqa: E731,E501
                        wgt.bind("<<ComboboxSelected>>", select_value)
            except TypeError:
                print('unsupported Widget Type??')
                print(w, w.__name__)
            # now, on each row apply the data
            for row in range(self.first_redraw_row, len(self.widgets)):
                apply(self.widgets[row][column], self.data[row][column])

    def _assign_row_data(self, idx, data=None):
        """
        Assign the data provided to the WidgetTable's data array's Variables.

        Parameters
        ----------
        idx : int
            Index to place the new data in the data array
        data : list | None
            Data to assign. This data is processed to ensure that it is in the
            right format for being assigned to the underlying Variables.
            This can consist of either the raw values for each widget, an
            instance of a Variable, or a dictionary with parameters as
            described by the docstring of the widget table.
            (see help(WidgetTable) for more info)
        """
        row_vars = []
        # iterate over the columns
        for i in range(len(self.pattern)):
            if data is not None:
                val = data[i]
            else:
                val = None
            if val is not None:
                if isinstance(self.pattern[i], dict):
                    # create a copy of the pattern for the current column data
                    new_dict = copy_dict(self.pattern[i])
                    # then populate the new dict with any provided data
                    if isinstance(val, Variable):
                        # in this case we are just receiving the Variable
                        # and don't want to modify the rest of the dictionary
                        new_dict['var'] = val
                        p = self.pattern[i]
                        if p.get('func_has_row_ctx', False):
                            f = copy(p['func'])
                            new_dict['func'] = lambda x=idx: f(x)
                    # TODO: handle the case of the raw data being passed
                    else:
                        # otherwise we have been passed a (at least partial)
                        # dictionary of data
                        if 'var' in val:
                            var = val['var']
                            if isinstance(var, Variable):
                                new_dict['var'] = var
                            else:
                                new_dict['var'].set(var)
                        if 'text' in val:
                            new_dict['text'] = val['text']
                        if 'func' in val:
                            if val.get('func_has_row_ctx', False):
                                # if the function requires knowledge of the row
                                # it is then we give it to it.
                                new_dict['func'] = lambda x=idx: val['func'](x)
                            else:
                                new_dict['func'] = val['func']
                        if 'configs' in val:
                            new_dict['configs'] = val['configs']
                    var = new_dict
                else:
                    if isinstance(val, Variable):
                        var = val
                    else:
                        var = self.pattern[i]()
                        var.set(val)
            else:
                if not isinstance(self.pattern[i], dict):
                    var = self.pattern[i]()
                else:
                    # we still need to check if the function requires row
                    # context
                    var = dict()
                    for key in self.pattern[i].keys():
                        if key != 'func':
                            var[key] = self.pattern[i][key]
                    if var.get('func_has_row_ctx', False):
                        var['func'] = lambda x=idx: self.pattern[i]['func'](x)
            row_vars.append(var)
        if idx < len(self.data):
            self.data[idx] = row_vars
        else:
            self.data.append(row_vars)

    def _assign_data(self, data):
        """
        This is used to assign raw data to the underlying variables
        """
        # clear self.data
        self.data = []
        for i, row in enumerate(data):
            self._assign_row_data(i, row)

    def _correct_idx_refs(self):
        """ Correct any reference to index in any function in the data array"""
        for i, row in enumerate(self.data):
            for val in row:
                if isinstance(val, dict):
                    if val.get('func_has_row_ctx', False):
                        f = copy(val['func'])
                        del val['func']
                        val['func'] = lambda x=i: f(x)

    def _create_widgets(self):
        """ Create all the base widgets required """
        if isinstance(self.add_options, list):
            add_option_frame = Frame(self)
            Label(add_option_frame, text="Add an option: ").grid(column=0,
                                                                 row=0,
                                                                 sticky='w')
            self.nameselection = Combobox(add_option_frame,
                                          values=self.add_options,
                                          state='readonly', exportselection=0)
            self.nameselection.grid(column=2, row=0, sticky='w')
            self.nameselection.bind("<<ComboboxSelected>>",
                                    self.add_row_from_selection)
            self.separator_offset = 1
            add_option_frame.grid(column=0, row=0, sticky='w', padx=2, pady=2)
            self.sf = ScrollableFrame(self)
            self.sf.grid(column=0, row=1, sticky='nsew')

            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(0, weight=1)
        else:
            self.sf = ScrollableFrame(self)
            self.sf.grid(column=0, row=0, sticky='nsew')
            if self.adder_script != DISABLED:
                self.add_button = Button(self.sf.frame, text="Add Row",
                                         command=self.add_row_from_button)
                self.add_button.grid(row=2, column=2 * self.num_columns - 1)
                self.add_button.bind(OSCONST.ADDROW, self._add_row_from_key)

            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
        for i, heading in enumerate(self.headings):
            Label(self.sf.frame, text=heading).grid(
                column=2 * i, row=self.separator_offset, sticky='nsew', padx=2,
                pady=2)
        Separator(self.sf.frame, orient='horizontal').grid(
            column=0, row=self.separator_offset + 1,
            columnspan=2 * self.num_columns - 1, sticky='ew')

        self.row_offset = self.sf.frame.grid_size()[1]

    def _draw_separators(self):
        """ Redraw all the separators when the table is being redrawn """
        rows = self.sf.frame.grid_size()[1]
        for i, sep in enumerate(self.separators):
            sep.grid_forget()
            sep.grid(column=2 * i + 1, row=self.separator_offset,
                     rowspan=rows - self.separator_offset, sticky='ns')

    def _resize_to_max(self, **config):
        """ Resize the ScrollCanvas up to the maximum allowed size if a max
        number of rows is specified.
        """
        max_x, max_y = (None, None)
        self.sf.update_idletasks()

        if self.max_rows is not None:
            if len(self.data) > self.max_rows:
                max_x, max_y = self.sf.frame.grid_bbox(
                    column=self.sf.frame.grid_size()[0],
                    row=self.max_rows + self.row_offset - 1)[:2]

        self.sf.block_resize = False
        self.sf.configure_view(max_size=(max_x, max_y), **config)

#region properties

    @property
    def options(self):
        return self.add_options

    @options.setter
    def options(self, value):
        if len(value) > 0:
            self.nameselection.configure(values=value)
            self.nameselection.set(value[0])

#region class methods

    #TODO: move to utils?
    @staticmethod
    def ensure_2D_array(arr):
        """ If the provided array is not 2D convert it to one """
        if isinstance(arr, list):
            if not isinstance(arr[0], list):
                return [arr]
            else:
                return arr
        else:
            raise ValueError("Provided data is not an array")
