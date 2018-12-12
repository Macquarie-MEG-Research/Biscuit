from tkinter import Variable, StringVar, IntVar


class OptionsVar(Variable):
    """Construct a string options variable.

    Parameters
    ----------
    master : widget
        The parent widget
    value : str
        The value from options to set as the currently selected value
        If this is not specified, the currently selected value defaults to
        the first element of options
    name : str
        An optional Tcl name (defaults to PY_VARnum).
    options : list
        A list of the options that the OptionsVar can have.
        If this changes and the currently selected value is no longer in
        the list of options then the value set will be the first element
        of options
    """
    def __init__(self, master=None, value=None, options=[], name=None):
        self._options = []

        Variable.__init__(self, master, value, name)

        for option in options:
            self._options.append(StringVar(value=str(option)))
        self._set_initial(value)

    def get(self):
        value = self._tk.globalgetvar(self._name)
        if isinstance(value, str):
            return value
        return str(value)

    def __len__(self):
        return len(self._options)

    def _set_initial(self, value):
        """ Set the value when a new instance of OptionsVar is created """
        if value is not None:
            self.set(value)
        else:
            if len(self) != 0:
                self._tk.globalsetvar(self._name, self._options[0].get())
            else:
                # set as empty string
                self._tk.globalsetvar(self._name, '')

    def set(self, value):
        """
        Set the variable to VALUE
        If there are options, then the set value must be in the available
        options.
        If there are no options the current value will be set to VALUE and it
        will be added to the list of possible values.
        """
        if self._options != []:
            for v in self._options:
                if value == v.get():
                    self._tk.globalsetvar(self._name, value)
                    break
            else:
                raise ValueError(
                    "Cannot set value {0}\n "
                    "Possible values: {1}".format(value, self.options))
        else:
            self._tk.globalsetvar(self._name, value)
            self._options.append(StringVar(value=str(value)))

    def append(self, value):
        """Append the value to the options list."""
        self._options.append(StringVar(value=str(value)))

    @property
    def options(self):
        return [v.get() for v in self._options]

    @options.setter
    def options(self, value):
        """Set the list of options."""
        # let's get the current value first, so that if it is in the current
        # list it will stay selected.
        curr_value = self._tk.globalgetvar(self._name)
        self._options = []
        for option in value:
            self._options.append(StringVar(value=str(option)))
        # also set the value to be the first one
        if curr_value != '' and curr_value in value:
            self._tk.globalsetvar(self._name, curr_value)
        elif len(self) != 0:
            self._tk.globalsetvar(self._name, self._options[0].get())
        else:
            # set as empty string
            self._tk.globalsetvar(self._name, '')


class StreamedVar(StringVar):
    """
    A custom Variable which can be used to capture redirected stdout's.
    This Variable will only update when the contents end with a newline
    character (indicating that the data has changed).
    Patterns can be provided to essentially filter the contents to only allow
    specific data to be set.

    Parameters
    ----------
    pattern : str | list of str
        A list of strings that are check to see if they are in the current
        value. The value is only set if the pattern is in the current
        value.
    process : function | dictionary: {str: function}
        A function which can be called to process the current value.
        This can be a dictionary to allow for processing of differently
        matched patterns.
    """
    def __init__(self, patterns=[], process=dict(), *args, **kwargs):
        super(StreamedVar, self).__init__(*args, **kwargs)
        self._curr_value = StringVar()
        #if pattern is not None:
        #    self.pattern = re.compile(pattern)
        self.pattern = patterns
        self.processing = process

    def write(self, value):
        if value != '\n':
            self.set(self.get() + value)
        else:
            #if re.match(self.pattern, self.get()):
            for pattern in self.pattern:
                if pattern in self.get():
                    func = self.processing.get(pattern, None)
                    if func is not None:
                        self.curr_value.set(func(self.get()))
                        self.set('')
                    else:
                        self.curr_value.set(self.get())
                        self.set('')
                    break
            else:
                self.set('')

    def get_curr(self):
        return self.curr_value.get()

    @property
    def curr_value(self):
        return self._curr_value


class RangeVar(IntVar):
    def __init__(self, master=None, value=None, name=None, max_val=0,
                 max_val_callback=None):
        self._max = max_val
        self._max_val_callback = max_val_callback

        Variable.__init__(self, master, value, name)

    def set(self, value):
        """
        Set the variable to VALUE
        If there are options, then the set value must be in the available
        options.
        If there are no options the current value will be set to VALUE and it
        will be added to the list of possible values.
        """
        if value > self.max:
            self._tk.globalsetvar(self._name, self.max)
        else:
            self._tk.globalsetvar(self._name, value)

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        self._max = value
        if self._max_val_callback is not None:
            self._max_val_callback()
