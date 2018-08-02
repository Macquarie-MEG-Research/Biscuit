from tkinter import Variable, StringVar


class StringOptsVar(Variable):

    def __init__(self, master=None, value=None, name=None, options=[]):
        """Construct a string options variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to "")
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """

        """ Value holder for lists of variables """
        self._options = []

        Variable.__init__(self, master, value, name)

        for option in options:
            self._options.append(StringVar(value=str(option)))
        # set the first value as the default one
        self._set_initial()

    def get(self):
        value = self._tk.globalgetvar(self._name)
        if isinstance(value, str):
            return value
        return str(value)

    def __len__(self):
        return len(self._options)

    def _set_initial(self):
        if len(self) != 0:
            self._tk.globalsetvar(self._name, self._options[0].get())

    def set(self, value):
        """ Set the variable to VALUE """
        for v in self._options:
            if value == v.get():
                self._tk.globalsetvar(self._name, value)
                break
        else:
            raise ValueError

    def append(self, value):
        """ Append the value to the options list """
        self._options.append(StringVar(value=str(value)))

    @property
    def options(self):
        return [v.get() for v in self._options]

    @options.setter
    def options(self, value):
        """ set the options anew """
        self._options = []
        for option in value:
            self._options.append(StringVar(value=str(option)))
        # also set the value to be the first one
        if len(self) != 0:
            self._tk.globalsetvar(self._name, self._options[0].get())


if __name__ == "__main__":
    from tkinter import Tk
    Tk()

    m = StringOptsVar(options=["hi", "there", "what"])
    print(m.options)
    m.set("hi")
    print(m.get())
    print(len(m))
    m.set("wow!!")
    print(m.get())
    print(len(m))
    print(m.options)
    n = StringOptsVar(options=['huh'])
    print(n.options)
