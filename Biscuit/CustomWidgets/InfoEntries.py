from tkinter import ALL
# import this specifically like this because we can actually set the bg colour
from tkinter import Entry as tkEntry
from tkinter import Checkbutton as tkCheckbutton
from tkinter.ttk import Label, Frame, Checkbutton, Combobox, Entry

from Biscuit.utils.utils import clear_widget
from Biscuit.Management import ToolTipManager
from Biscuit.utils.constants import OSCONST

ttm = ToolTipManager()


class InfoMaster():
    def __init__(self, master, label, value, validate_cmd=None):
        self._master = master

        self._label = Label(self._master, text="{0}: ".format(label))
        self._value = value

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
        pass

    def tooltip(self, text):
        """ Register the text specified with the tool tip manager (ttm) for
        both label and value widgets """
        ttm.register(self.label, text)
        ttm.register(self.value, text)

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

    @value.setter
    def value(self, value):
        self._set_value(value)


class ValidatedEntry(tkEntry):
    """
    An entry widget that will have a certain background colour
    if the value entered is not valid.

    Parameters
    ----------
    master : instance of Widget
        Master widget this belongs to.
    bad_values : list
        List of values which are recognised as "bad". If the value in the entry
        is in this list the background colour is set to the `bad_colour`.
    good_colour : str
        Colour to set the background when the entered value is not "bad".
    bad_colour : str
        Colour to set the background when the entered value is "bad".
    validate_cmd : function
        Function used as a callback. This is called when the value changes.
    force_dtype : str | one of ('int', 'alnum')
        The data type to force entry to.
        If 'int' then only numeric values can be entered.
        If 'alnum' then only alphanumeric characters can be entered
        ([a-zA-Z0-9])
    """
    def __init__(self, master, bad_values=[], good_colour="White",
                 bad_colour="Red", validate_cmd=None, force_dtype=None,
                 *args, **kwargs):
        super(ValidatedEntry, self).__init__(master, *args, **kwargs)

        self.bad_values = bad_values
        self.good_colour = good_colour
        self.bad_colour = bad_colour
        self.validate_cmd = validate_cmd
        self.force_dtype = force_dtype

        self._is_valid = True

        vcmd = self.register(self._set_background)
        self.configure(validate=ALL, validatecommand=(vcmd, '%P', '%s'))

    def _set_background(self, value_if_allowed, prior_value):
        if self.force_dtype:
            if self.force_dtype == 'int':
                if not value_if_allowed.isdigit() and value_if_allowed != '':
                    return False
            elif self.force_dtype == 'alnum':
                if not value_if_allowed.isalnum() and value_if_allowed != '':
                    return False
        if value_if_allowed not in self.bad_values:
            self.is_valid = True
        else:
            self.is_valid = False
        # finally, run the provided extra validation function
        # TODO: pass value_if_allowed to validate_cmd
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
    # TODO: add docstring here
    A custom entry box that will automatically return a ValidatedEntry
    box if bad values are specified
    """
    def __init__(self, master, label, value, validate_cmd=None, bad_values=[],
                 force_dtype=None):
        super(InfoEntry, self).__init__(master, label, value, validate_cmd)
        self.bad_values = bad_values

        # draw the label and entry box
        if bad_values == []:
            self._value = Entry(self._master, textvariable=value)
        else:
            self._value = ValidatedEntry(self._master, bad_values=bad_values,
                                         textvariable=value,
                                         highlightbackground='#E9E9E9',
                                         validate_cmd=validate_cmd,
                                         force_dtype=force_dtype)

    def check_valid(self):
        if isinstance(self._value, ValidatedEntry):
            self._value.check_valid()

    def _set_value(self, value):
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
        self._value.config(text="{0}".format(value))


class InfoCheck(InfoMaster):
    def __init__(self, master, value, label, validate_cmd=None):
        super(InfoCheck, self).__init__(master, value, label, validate_cmd)

        #self._label = Label(self._master, text="{0}: ".format(data[0]))
        if OSCONST.os == 'LNX':
            self._value = tkCheckbutton(self._master, variable=value,
                                        command=self._validate_cmd)
        else:
            self._value = Checkbutton(self._master, variable=value,
                                      command=self._validate_cmd)

    def _set_value(self, value):
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
            # In this case a Variable that isn't an OptionsVar has probably
            # been passed. Just do some default values.
            self._value = Combobox(self._master, values=['Error', 'Values'],
                                   state='readonly')
        self._value.set(self.optVar.get())
        self._value.bind("<<ComboboxSelected>>", self.select_value)

        self._value.bind('<KeyPress>', self._select_from_key)

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

    def _select_from_key(self, *args):
        """ select the first entry starting with the entered key """
        # TODO: make it continue through them?
        char = args[0].char.upper()
        for opt in self.optVar.options:
            if opt.upper().startswith(char):
                self.optVar.set(opt)
                self._value.set(self.optVar.get())
                break
