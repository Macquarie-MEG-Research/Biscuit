from tkinter import PhotoImage, Checkbutton, Variable
from tkinter import Button as tkButton
from tkinter.ttk import Label, Separator, Button, Frame, Entry, Combobox
from platform import system as os_name


class WidgetTable(Frame):
    """
    A frame which contains rows which can be populate with multiple
    widgets in each column.
    We can have a button to remove rows, and a few different ways to add new
    rows.
    """
    def __init__(self, master, headings=[], row_vars=[], row_configs=[],
                 entry_types=[], add_options=None, data_array=[],
                 adder_script=None, remove_script=None, *args, **kwargs):
        """
        Arguments:
        - headings - A list of strings for the headings
        - row_vars - A list of Variables to be associated with the widget.
            These variables need to be the appropriate type for the
            entry_type associated with the data, as well as the data passed in
            (if the table is to be initially or automatically populated)
            A tuple of the form (string, function) can be used as the
            "variable" for a button widget.
        - row_configs - A list of dictionaries.
        - entry_types - A list of Widgets that will be drawn in each column.
        - add_options - A fixed length list of options that can be added.
            If None then the rows can just be added arbitrarily using button.
        - data_array - A list of the intial data to populate the table with.
        - adder_script - A function that will be called when the Add button is
            pressed or a value is picked from the add_options option box.
            If this function returns an values they are assumed to be the
            values to be passed into the newly created widgets if possible.
        - remove_script - A callback for when a row is deleted
        """

        self.master = master

        super(WidgetTable, self).__init__(self.master, *args, **kwargs)

        self.rows = []
        self.headings = headings
        self.row_vars = row_vars
        self.row_configs = row_configs
        self.entry_types = entry_types
        self.num_columns = len(self.headings)
        self.add_options = add_options
        self.adder_script = adder_script
        self.remove_script = remove_script

        self.row_offset = 0
        self.separator_offset = 0

        self.separators = []
        for _ in range(self.num_columns - 1):
            sep = Separator(self, orient='vertical')
            self.separators.append(sep)

        if os_name() == 'Windows':
            from PIL import Image, ImageTk
            self.delete_icon = Image.open("assets/remove_row_trans.png")
            self.delete_icon = self.delete_icon.resize((20, 20), Image.LANCZOS)
            self.delete_icon = ImageTk.PhotoImage(self.delete_icon)
        else:
            self.delete_icon = PhotoImage(file="assets/remove_row.png")

        self._create_widgets()
        self._draw_separators()
        # maybe utilise the set method?
        if data_array is not []:
            for row in data_array:
                self.add_row(row)

    def _create_widgets(self):
        if isinstance(self.add_options, list):
            Label(self, text="Add an option: ").grid(column=0,
                                                     row=0, sticky='w')
            self.nameselection = Combobox(self, values=self.add_options,
                                          state='readonly', exportselection=0)
            self.nameselection.grid(column=2, row=0, sticky='w')
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
                                           sticky='nsew')
        Separator(self, orient='horizontal').grid(
            column=0, row=self.separator_offset + 1,
            columnspan=2 * self.num_columns - 1, sticky='ew')

        self.row_offset = self.grid_size()[1]
        #print('original offset: {0}'.format(self.row_offset))

    def add_row(self, data=[]):
        row_data = []
        row_widgets = []
        if self.add_button is not None:
            self.add_button.grid_forget()
        rows = self.grid_size()[1]
        for i in range(self.num_columns):
            if data != []:
                # allow only some values to be set
                if isinstance(data[i], (tuple, Variable)):
                    var = data[i]
                else:
                    if isinstance(self.row_vars[i], tuple):
                        var = self.row_vars[i]
                    else:
                        var = self.row_vars[i]()
                        var.set(data[i])
            else:
                var = self.row_vars[i]()
            row_data.append(var)
            w = self.entry_types[i](self)
            if isinstance(w, (Entry, Label)):
                w.configure(textvariable=var)
            if isinstance(w, Checkbutton):
                w.configure(variable=var, command=None)
            elif isinstance(w, Button):
                w.configure(text=var[0], command=var[1])
            row_widgets.append(w)
            w.grid(row=rows, column=2 * i, sticky='nsew')
        curr_row = len(self.rows)
        print('current row: {0}'.format(curr_row))
        delete_button = tkButton(
            self, command=lambda x=curr_row: self.delete_row(x),
            relief='flat', borderwidth=0, highlightthickness=0)
        delete_button.config(image=self.delete_icon)
        delete_button.grid(row=rows, column=2 * self.num_columns - 1)
        row_widgets.append(delete_button)
        self.rows.append((row_data, row_widgets))
        self._draw_separators()
        if self.add_button is not None:
            self.add_button.grid(row=rows + 1, column=2 * self.num_columns - 1)
        #self.row_offset = self.grid_size()[1] - len(self.rows)

    def delete_row(self, idx):
        #print('offset: {0}'.format(self.row_offset))
        print('deleting row {0}'.format(idx))
        if self.remove_script is not None:
            self.remove_script(idx)
        for w in self.rows[idx][1]:
            w.grid_forget()
        del self.rows[idx]
        for i in range(len(self.rows)):
            del_btn = self.rows[i][1][-1]
            del_btn.config(command=lambda x=i: self.delete_row(x))
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
                w.grid(row=rows, column=2 * i, sticky='nsew')
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
        # this only needs to be different to implement the functionality to
        # allow the entry in the list to be removed if it needs to be
        # unless we leave that functionality up to the user...
        if self.adder_script is not None:
            try:
                ret = self.adder_script()
                print(ret)
                if ret is None:
                    self.add_row()
                else:
                    self.add_row(ret)
            except:
                pass

    def get(self, values=True):
        """
        Return a 2D array of all the data contained.
        If values == True (default), the value of the Variables will be
        returned. If False the Variables themselves will be returned
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

    def set_row_vars(self, idx, vars, configs=[]):
        """
        Set the data for a specific row
        Inputs:
        - idx - index of the row
        - vars - row data (as dictionaries)
        """
        for i in range(self.num_columns):
            val = vars[i]
            if val is not None:
                self.rows[idx][0][i] = val
                self._set_widget_var(self.rows[idx][1][i], val)
                # unpack dictionary as argument
                if configs != []:
                    #print(configs)
                    if isinstance(configs[i], dict):
                        self.rows[idx][1][i].config(**configs[i])

    @staticmethod
    def _set_widget_var(w, var):
        if isinstance(var, tuple):
            # in this case the second value is the command
            command = var[1]
            data = var[0]
        else:
            command = None
            data = var
        if isinstance(w, (Entry, Label)):
            w.configure(textvariable=data)
        elif isinstance(w, Checkbutton):
            w.configure(variable=data, command=command)
        elif isinstance(w, Button):
            w.configure(text=data, command=command)

    def set(self, data, configs):
        """
        This can be used to force overwrite the current data in the Table.
        """
        diff = len(data) - len(self.rows)
        if diff < 0:
            # remove all unneccesary rows
            for _ in range(abs(diff)):
                self.delete_row(-1)
        elif diff > 0:
            # add the required number of rows:
            for _ in range(diff):
                self.add_row()
        # now that we have the correct number of rows, populate them
        for i in range(len(data)):
            self.set_row_vars(i, data[i], configs[i])

    def curr_row(self):
        a = self.focus_get().grid_info().get('row') - self.row_offset
        print('curr row: {0}'.format(a))
        return a

    @property
    def options(self):
        return self.add_options

    @options.setter
    def options(self, value):
        self.add_options = value
        self.nameselection.configure(values=self.add_options)
