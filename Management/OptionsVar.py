from tkinter import Variable, StringVar


class OptionsVar(Variable):

    def __init__(self, master=None, value=None, options=[], name=None):
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

        """ Value holder for lists of variables """
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
        """ Append the value to the options list """
        self._options.append(StringVar(value=str(value)))

    @property
    def options(self):
        return [v.get() for v in self._options]

    @options.setter
    def options(self, value):
        """ set the options anew """
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


if __name__ == "__main__":
    from tkinter import Tk
    Tk()

    m = OptionsVar(options=["hi", "there", "what"])
    print(m.options)
    m.set("hi")
    print(m.get())
    print(len(m))
    m.set("wow!!")
    print(m.get())
    print(len(m))
    print(m.options)
    n = OptionsVar(options=['huh'])
    print(n.options)
