from tkinter import ALL
# import this specifically like this because we can actually set the bg colour
from tkinter import Entry as tkEntry
from tkinter.ttk import Label, Checkbutton, Frame, Combobox
from utils import clear_widget


class InfoMaster():
    def __init__(self, master, label, value, validate_cmd=None):
        self._master = master

        self._label = Label(self._master, text="{0}: ".format(label))
        self._value = value

        #self._data = data

        self._validate_cmd = validate_cmd

    def set_bads_callback(self, bad_values=None, associated_data=None):
        pass

    def validate(self):
        """
        A function to call the validation method for the associated file
        """
        if self._validate_cmd is not None:
            self._validate_cmd()

    def _set_value(self, value):
        """ a method to be overwridden by other classes """
        #self._label.config(text="{0}: ".format(self._data[0]))
        pass

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label.config(text="{0}: ".format(value))

    @property
    def value(self):
        return self._value

    @property
    def master(self):
        return self._master

    """
    @property
    def data(self):
        return self._data
    """

    @value.setter
    def value(self, value):
        self._set_value(value)


class ValidatedEntry(tkEntry):
    """
    An entry widget that will have a certain background colour
    if the value entered is not valid.
    """
    def __init__(self, master, bad_values=[], good_colour="White",
                 bad_colour="Red",
                 validate_cmd=None, *args, **kwargs):
        super(ValidatedEntry, self).__init__(master, *args, **kwargs)

        self.bad_values = bad_values
        self.good_colour = good_colour
        self.bad_colour = bad_colour
        self.validate_cmd = validate_cmd

        self._is_valid = True

        vcmd = self.register(self._set_background)
        self.configure(validate=ALL, validatecommand=(vcmd, '%P', '%s'))

    def _set_background(self, value_if_allowed, prior_value):
        if value_if_allowed not in self.bad_values:
            self.is_valid = True
        else:
            self.is_valid = False
        # finally, run the provided extra validation function
        if self.validate_cmd is not None:
            self.validate_cmd()
        return True

    def check_valid(self):
        if self.get() not in self.bad_values:
            self.is_valid = True
        else:
            self.is_valid = False

    @property
    def is_valid(self):
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value):
        if value is True:
            self.config({'background': self.good_colour})
        elif value is False:
            self.config({'background': self.bad_colour})
        else:
            raise ValueError
        self._is_valid = value


class InfoEntry(InfoMaster):
    """
    A custom entry box that will automatically return a ValidatedEntry
    box if bad values are specified
    """
    def __init__(self, master, label, value, validate_cmd=None, bad_values=[]):
        super(InfoEntry, self).__init__(master, label, value, validate_cmd)
        self.bad_values = bad_values

        # draw the label and entry box
        #self._label = Label(self._master, text="{0}: ".format(data[0]))
        if bad_values == []:
            self._value = tkEntry(self._master, textvariable=value)
        else:
            self._value = ValidatedEntry(self._master, bad_values=bad_values,
                                         textvariable=value,
                                         validate_cmd=validate_cmd)

    def check_valid(self):
        if isinstance(self._value, ValidatedEntry):
            self._value.check_valid()

    def _set_value(self, value):
        #super(InfoEntry, self)._set_value(value)
        self._value.config(textvariable=value)

    @property
    def validate_cmd(self):
        return self._validate_cmd

    @validate_cmd.setter
    def validate_cmd(self, value):
        # pass the new validate_cmd to the validated entry if required
        if value is not None:
            self._validate_cmd = value
            if isinstance(self._value, ValidatedEntry):
                self._value.validate_cmd = value


class InfoLabel(InfoMaster):
    def __init__(self, master, label, value, validate_cmd=None):
        super(InfoLabel, self).__init__(master, label, value, validate_cmd)

        # draw the label and entry box
        #self._label = Label(self._master, text="{0}: ".format(data[0]))
        self._value = Label(self._master, text=value)

    def _set_value(self, value):
        #super(InfoLabel, self)._set_value(value)
        self._value.config(text="{0}".format(value))


class InfoCheck(InfoMaster):
    def __init__(self, master, value, label, validate_cmd=None):
        super(InfoCheck, self).__init__(master, value, label, validate_cmd)

        #self._label = Label(self._master, text="{0}: ".format(data[0]))
        self._value = Checkbutton(self._master, variable=value,
                                  command=self._validate_cmd)

    def _set_value(self, value):
        #super(InfoCheck, self)._set_value(value)
        self._value.config(variable=value)

    @property
    def validate_cmd(self):
        return self._validate_cmd

    @validate_cmd.setter
    def validate_cmd(self, value):
        # pass the new validate_cmd to the validated entry if required
        self._validate_cmd = value
        self._value.config(command=self._validate_cmd)


class InfoList(InfoMaster):
    def __init__(self, master, label, value, validate_cmd=None):
        super(InfoList, self).__init__(master, label, value, validate_cmd)

        #self._label = Label(self._master, text="{0}: ".format(data[0]))
        self._value = Frame(self._master)
        self._draw_list(value)
        self._value.grid()

    def _draw_list(self, list_data):
        clear_widget(self._value)
        if len(list_data) != 0:
            for value in list_data:
                # consider just labels for now...
                # make the wrap length dynamic?? Ref'd to the parent size?
                lbl = Label(self._value, text=value, wraplength=400)
                lbl.grid(row=self._value.grid_size()[1])      # add to the end
        else:
            lbl = Label(self._value, text="None", foreground="Red")
            lbl.grid(row=self._value.grid_size()[1])

    def _set_value(self, value):
            #super(InfoList, self)._set_value(value)
            self._draw_list(value)
            self._value.grid()


class InfoChoice(InfoMaster):
    def __init__(self, master, label, value):
        super(InfoChoice, self).__init__(master, label, value)
        self.optVar = value

        #self._label = Label(self._master, text="{0}: ".format(data[0]))
        try:
            self._value = Combobox(self._master, values=self.optVar.options,
                                   state='readonly')
        except AttributeError:
            # In this case a Variable that isn't an StringOptsVar has probably
            # been passed. Just do some default values.
            self._value = Combobox(self._master, values=['Error', 'Values'],
                                   state='readonly')
        self._value.set(self.optVar.get())
        self._value.bind("<<ComboboxSelected>>", self.select_value)

    def select_value(self, event):
        self.optVar.set(self._value.get())

    def _set_value(self, value):
        self.optVar = value
        self._value.set(self.optVar.get())
        self._value.config(values=self.optVar.options)

    def bind(self, event, func):
        # allow external overriding of the bind event
        self.select_value(event)
        self._value.bind(event, func)
