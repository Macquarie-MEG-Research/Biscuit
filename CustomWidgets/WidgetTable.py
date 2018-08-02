from tkinter import Entry, Frame, PhotoImage
from tkinter.ttk import Style, Label, Separator, Checkbutton, Button
from OptionVars import StringOptsVar
from InfoEntries import InfoChoice


class WidgetTable(Frame):
    """
    A frame which contains rows which can be populate with multiple
    widgets in each column.
    We can have a button to remove rows, and a few different ways to add new
    rows.
    """
    def __init__(self, master, headings=[], row_vars=[], entry_types=[],
                 add_options=None, data_array=[], adder_script=None, *args,
                 **kwargs):
        """
        Arguments:
        - headings - A list of strings for the headings
        - row_vars - A list of Variable types that will be instantiated
            for each widget in the row to track the data.
            These variables need to be the appropriate type for the
            entry_type associated with the data, as well as the data passed in
            (if the table is to be initially or automatically populated)
            A tuple of the form (string, function) can be used as the
            "variable" for a button widget.
        - entry_types - A list of Widgets that will be drawn in each column.
        - add_options - A StringOptsVar object that has a fixed length list of
            options that can be added.
            If None then the rows can just be added arbitrarily using button.
        - data_array - A list of the intial data to populate the table with.
        - adder_script - A function that will be called when the Add button is
            pressed or a value is picked from the add_options option box.
            If this function returns an values they are assumed to be the
            values to be passed into the newly created widgets if possible.
        """
        # need a mapping to determine how the options are used to populate the
        # list...

        self.master = master

        super(WidgetTable, self).__init__(self.master, *args, **kwargs)

        self.rows = []
        self.headings = headings
        self.row_vars = row_vars
        self.entry_types = entry_types
        self.num_columns = len(self.headings)
        self.add_options = add_options
        self.adder_script = adder_script

        self.row_offset = 0
        self.separator_offset = 0

        self.separators = []
        for _ in range(self.num_columns - 1):
            sep = Separator(self, orient='vertical')
            self.separators.append(sep)

        self.delete_icon = PhotoImage(file="assets/remove_row.png")

        self.t_style = Style()
        self.t_style.configure('Transp.TButton', borderwidth=0, relief='flat',
                               padding=0)

        self._create_widgets()
        self._draw_separators()
        if data_array is not []:
            for row in data_array:
                self.add_row(row)

    def _create_widgets(self):
        if isinstance(self.add_options, StringOptsVar):
            Label(self, text="Add an option: ").grid(column=0,
                                                     row=0, sticky='w')
            self.nameselection = InfoChoice(self, "", self.add_options)
            self.nameselection.value.grid(column=2, row=0, sticky='w')
            self.nameselection.bind("<<ComboboxSelected>>",
                                    self.add_row_from_selection)
            self.separator_offset = 1
            self.add_button = None
        else:
            self.add_button = Button(self, text="Add Row",
                                     command=self.add_row_from_button)
            self.add_button.grid(row=2, column=2 * self.num_columns - 1)
        for i, heading in enumerate(self.headings):
            Label(self, text=heading).grid(column=2 * i,
                                           row=self.separator_offset,
                                           sticky='w')
        Separator(self, orient='horizontal').grid(
            column=0, row=self.separator_offset + 1,
            columnspan=2 * self.num_columns - 1, sticky='ew')

    def add_row(self, data=[]):
        row_data = []
        row_widgets = []
        if self.add_button is not None:
            self.add_button.grid_forget()
        rows = self.grid_size()[1]
        for i in range(self.num_columns):
            if not isinstance(self.row_vars[i], tuple):
                var = self.row_vars[i]()
            else:
                var = self.row_vars[i]
            if data != []:
                # allow only some values to be set
                if data[i] is not None:
                    var.set(data[i])
            row_data.append(var)
            w = self.entry_types[i](self)
            if isinstance(w, (Entry, Checkbutton, Label)):
                w.configure(textvariable=var)
            elif isinstance(w, Button):
                w.configure(text=var[0], command=var[1])
            row_widgets.append(w)
            w.grid(row=rows, column=2 * i)
        delete_button = Button(self, command=self.delete_row,
                               style='Transp.TButton')
        delete_button.config(image=self.delete_icon)
        delete_button.grid(row=rows, column=2 * self.num_columns - 1)
        row_widgets.append(delete_button)
        self.rows.append((row_data, row_widgets))
        self._draw_separators()
        if self.add_button is not None:
            self.add_button.grid(row=rows + 1, column=2 * self.num_columns - 1)
        self.row_offset = self.grid_size()[1] - len(self.rows)

    def delete_row(self):
        i = self.focus_get().grid_info().get('row') - self.row_offset + 1
        for w in self.rows[i][1]:
            w.grid_forget()
        del self.rows[i]
        self.draw_rows()

    def draw_rows(self):
        # redraw all the row widgets
        # this can be optimised to only redraw objects after the deletion
        # index. WIll also remove some redraw flickering

        # first remove all the data
        for row in self.rows:
            for w in row[1]:
                w.grid_forget()
        # also get rid of the separators:
        for sep in self.separators:
            sep.grid_forget()
        # get rid of the add button if it is there
        if self.add_button is not None:
            self.add_button.grid_forget()
        # now add the rows back
        for row in self.rows:
            rows = self.grid_size()[1]
            for i, w in enumerate(row[1][:-1]):
                # skip the delete button
                w.grid(row=rows, column=2 * i)
            # draw it separately
            row[1][-1].grid(row=rows, column=2 * self.num_columns - 1)
        rows = self.grid_size()[1]
        self._draw_separators()
        if self.add_button is not None:
            self.add_button.grid(row=rows + 1, column=2 * self.num_columns - 1)

    def _draw_separators(self):
        rows = self.grid_size()[1]
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
                    self.add_row()
                else:
                    self.add_row(ret)
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
            self.add_row()

    def add_row_from_selection(self, event):
        self.add_row()

    def get(self, values=True):
        """
        Return a 2D array of all the data contained.
        If values == True (default), the value of the Variables will be
        returned. If False the Variables themselves will be returned
        If flatten == True the array returned will be 1D
        """
        out_data = []
        for row in self.rows:
            row_data = []
            if values:
                for var in row[0]:
                    if not isinstance(var, tuple):
                        row_data.append(var.get())
                    else:
                        # not sure what to do about button data.
                        # For now, just return the string
                        row_data.append(var[0])
            else:
                row_data.append(row[0])
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
                self.rows[idx][0][i].set(val)

    def set(self, data):
        """
        This can be used to force overwrite the current data in the Table.
        """
        self.rows = data
        if len(data) != len(self.rows):
            # only redraw if the number of rows has changed
            self.draw_rows()

    def curr_row(self):
        return self.focus_get().grid_info().get('row') - self.row_offset + 1
