from tkinter import Checkbutton, Variable
from tkinter import Button as tkButton
from tkinter.ttk import Label, Separator, Button, Frame, Entry, Combobox
from PIL import Image, ImageTk
# import copy so we can create static copies of the reference functions in the
# underlying pattern of a row if any.
from copy import copy

from .ScrollableFrame import ScrollableFrame


class WidgetTable(Frame):
    """
    A frame which contains rows which can be populate with multiple
    widgets in each column.
    We can have a button to remove rows, and a few different ways to add new
    rows.
    """
    def __init__(self, master, headings=[], pattern=[], widgets_pattern=[],
                 add_options=None, data_array=[], adder_script=None,
                 remove_script=None, sort_column=None, *args, **kwargs):
        """
        Arguments:
        - headings - A list of strings for the headings
        - pattern - A list of Variables to be associated with the widget.
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
        - widgets_pattern - A list of Widgets that will be drawn in each
            column.
            These widgets *must* be un-instantiated to allow cloning when
            creating new rows.
        - add_options - A fixed length list of options that can be added.
            If None then the rows can just be added arbitrarily using button.
        - data_array - A list of the intial data to populate the table with.
            This can either be raw data or an array of the variables
        - adder_script - A function that will be called when the Add button is
            pressed or a value is picked from the add_options option box.
            If this function returns an values they are assumed to be the
            values to be passed into the newly created widgets if possible.
        - remove_script - A callback for when a row is deleted
        - sort_column - The column number that the data will automatically be
            sorted by.
        """

        self.master = master

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

        # the index we need to redraw the rows after
        self.first_redraw_row = 0

        self.row_offset = 0
        self.separator_offset = 0

        self.widgets = []
        self._create_widgets()

        self.separators = []
        for _ in range(self.num_columns - 1):
            sep = Separator(self.sf.frame, orient='vertical')
            self.separators.append(sep)

        self.delete_icon = Image.open("assets/remove_row_trans.png")
        self.delete_icon = self.delete_icon.resize((20, 20), Image.LANCZOS)
        self.delete_icon = ImageTk.PhotoImage(self.delete_icon)

        # storage variables
        if data_array != []:
            # ensure a 2D array
            if not isinstance(data_array[0], list):
                data_array = [data_array]
            # generate all the widgets
            self.add_row_widgets(len(data_array))
            # now assign the data to self.data
            self._assign_data(data_array)
            self.sort_data()
            self._apply_data()
        else:
            # empty table
            self.data = []
            self._draw_separators()

    def _create_widgets(self):
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
            self.add_button = None
            add_option_frame.grid(column=0, row=0)
            self.sf = ScrollableFrame(self)
            self.sf.grid(column=0, row=1, sticky='nsew')
        else:
            self.sf = ScrollableFrame(self)
            self.sf.grid(column=0, row=1, sticky='nsew')
            self.add_button = Button(self.sf.frame, text="Add Row",
                                     command=self.add_row_from_button)
            self.add_button.grid(row=2, column=2 * self.num_columns - 1)
        for i, heading in enumerate(self.headings):
            Label(self.sf.frame, text=heading).grid(
                column=2 * i, row=self.separator_offset, sticky='nsew')
        Separator(self.sf.frame, orient='horizontal').grid(
            column=0, row=self.separator_offset + 1,
            columnspan=2 * self.num_columns - 1, sticky='ew')

        self.row_offset = self.sf.frame.grid_size()[1]

    def add_row_data(self, idx, data=None):
        """
        Take the data provided in `data` and add it to the list of data
        for the entire table.
        Paramaters:
        - data : list
            This is a list of either the values the variables will take or the
            data itself.
            Any entry can be None which indicates the default un-initiated data
            should be used
        """
        self.first_redraw_row = 0  # len(self.data) - 1
        self._assign_row_data(idx, data)

    def add_row_widgets(self, count=1):
        # remove the add button if it exsists
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
                w_actual.grid(row=rows, column=2 * i, sticky='nsew')
                row_widgets.append(w_actual)

            # add the delete button at the end of the row
            curr_row = initial_rows + r
            delete_button = tkButton(
                self.sf.frame,
                command=lambda x=curr_row: self.delete_rows_and_update(x),
                relief='flat', borderwidth=0, highlightthickness=0)
            delete_button.config(image=self.delete_icon)
            delete_button.grid(row=rows, column=2 * self.num_columns - 1)
            row_widgets.append(delete_button)
            self.widgets.append(row_widgets)

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
        """
        refresh = False

        # if from_start == True then the data will be placed from row 0
        curr_rows = (1 - from_start) * len(self.data)
        # if there is no size difference we simply want to refresh the data
        if count == 0:
            refresh = True
            count = len(data)
        if data is not None:
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

    def _assign_row_data(self, idx, data=None):
        """
        If data is provided apply it to an appropriately constructed
        list and return the list
        """
        row_vars = []
        for i in range(len(self.pattern)):
            if data is not None:
                val = data[i]
            else:
                val = None
            if val is not None:
                if isinstance(self.pattern[i], dict):
                    # create a copy of the pattern for the current column data
                    new_dict = self.pattern[i].copy()
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
                    var = self.pattern[i]
                    if var.get('func_has_row_ctx', False):
                        f = copy(var['func'])
                        var['func'] = lambda x=idx: f(x)
            row_vars.append(var)
        if idx < len(self.data):
            self.data[idx] = row_vars
        else:
            self.data.append(row_vars)

    def _assign_data(self, data):
        """
        This is used to assign raw data to the underlying variables
        If data is passed as variables already this isn't ever used
        """
        # clear self.data
        self.data = []
        for i, row in enumerate(data):
            self._assign_row_data(i, row)

    def _apply_data(self):
        """
        Takes all the data and applies them to all the rows from the last
        changed one onwards
        """
        # do columns then rows to save having to check data types repeatedly
        for column in range(self.num_columns):
            # first, create a lambda which can be re-used for each row
            w = self.widgets_pattern[column]
            try:
                if issubclass(w, (Entry, Label)):
                    if isinstance(self.pattern[column], dict):
                        # apply any provided configs:
                        apply = lambda wgt, var: wgt.configure(
                            textvariable=var['var'],
                            **var.get('configs', dict()))
                    else:
                        apply = lambda wgt, var: wgt.configure(
                            textvariable=var)
                if issubclass(w, Checkbutton):
                    # check underlying data type to provide correct function
                    if isinstance(self.pattern[column], dict):
                        apply = lambda wgt, var: wgt.configure(
                            variable=var['var'], command=var.get('func', None),
                            **var.get('configs', dict()))
                    else:
                        apply = lambda wgt, var: wgt.configure(variable=var)
                elif issubclass(w, Button):
                    apply = lambda wgt, var: wgt.configure(text=var['text'],
                                                           command=var['func'])
            except TypeError:
                print('unsupported Widget Type??')
                print(w, w.__name__)
            # now, on each row apply the data
            for row in range(self.first_redraw_row, len(self.widgets)):
                apply(self.widgets[row][column], self.data[row][column])

    def _correct_idx_refs(self):
        # this iterates over the data and fixes up any functions that require a
        # reference to their row number
        for i, row in enumerate(self.data):
            for val in row:
                if isinstance(val, dict):
                    if val.get('func_has_row_ctx', False):
                        f = copy(val['func'])
                        del val['func']
                        val['func'] = lambda x=i: f(x)

    def delete_row(self, idx, ignore_script=False):
        """ Remove the row widgets and data """
        if self.remove_script is not None and not ignore_script:
            self.remove_script(idx)
        for w in self.widgets[-1]:
            w.grid_forget()
        del self.widgets[-1]
        del self.data[idx]

    def delete_rows_and_update(self, idx, count=1, ignore_script=False):
        """ Removes the row and updates all the required info """
        # remove up to the maximum number of rows
        for _ in range(min(len(self.widgets), count)):
            self.delete_row(idx, ignore_script)
        # remap the delete command for the buttons
        for i in range(len(self.widgets)):
            del_btn = self.widgets[i][-1]
            del_btn.config(command=lambda x=i: self.delete_rows_and_update(x))
        # now, reapply all the variables
        self.first_redraw_row = idx
        self._correct_idx_refs()
        self._apply_data()
        self.sf.configure_view()

    def _draw_separators(self):
        rows = self.sf.frame.grid_size()[1]
        for i, sep in enumerate(self.separators):
            sep.grid_forget()
            sep.grid(column=2 * i + 1, row=self.separator_offset,
                     rowspan=rows - self.separator_offset, sticky='ns')

    def add_row_from_button(self):
        # before anything happens call the adder script if there is one:
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
        self.sf.configure_view(move_to_bottom=True)

    def add_row_from_selection(self, event):
        # this only needs to be different to implement the functionality to
        # allow the entry in the list to be removed if it needs to be
        # unless we leave that functionality up to the user...
        if self.adder_script is not None:
            ret = self.adder_script()
            if ret is None:
                self.add_rows()
            else:
                self.add_rows(ret)
        self.sf.configure_view()

    def get(self, values=True):
        """
        Return a 2D array of all the data contained.
        If values == True (default), the value of the Variables will be
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

    def set_row(self, idx, data):
        """
        Set the data for a specific row
        Inputs:
        - idx - index of the row
        - data - row data (as values, not Variables)
        """
        for i, val in enumerate(data):
            if val is not None:
                self.data[idx][i].set(val)

    def sort_data(self):
        if isinstance(self.sort_column, int):
            if self.sort_column < self.num_columns:
                self.data.sort(key=lambda x: x[self.sort_column].get())

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

        self.sf.configure_view()

    def curr_row(self):
        a = self.focus_get().grid_info().get('row') - self.row_offset
        return a

    @property
    def options(self):
        return self.add_options

    @options.setter
    def options(self, value):
        if len(value) > 0:
            self.nameselection.configure(values=value)
            self.nameselection.set(value[0])

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
